from pathlib import Path
from tempfile import TemporaryDirectory

from app.storage import PostgresStore


class FakeCursor:
    def __init__(self) -> None:
        self.queries = []
        self.inserted_chunks = []
        self.updated_chunks = []
        self.deleted_document_ids = []
        self._fetchone = None
        self.last_query = ""

    def execute(self, query, params=None):
        self.last_query = query
        self.queries.append((query, params))
        if "insert into document_chunks" in query:
            self.inserted_chunks.append(params)
        if "update document_chunks" in query:
            self.updated_chunks.append(params)
        if "delete from document_chunks" in query:
            self.deleted_document_ids.append(params[0])
        if "returning id" in query:
            self._fetchone = ("document-1",)

    def fetchone(self):
        result = self._fetchone
        self._fetchone = None
        return result

    def fetchall(self):
        return []


class FakeConnection:
    def __init__(self, cursor: FakeCursor) -> None:
        self.cursor_value = cursor

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def cursor(self):
        return self.cursor_value


class FakeEmbeddingClient:
    enabled = True

    def embed_texts(self, texts):
        return [[0.1] * 1024 for _ in texts]


class BackfillCursor(FakeCursor):
    def execute(self, query, params=None):
        super().execute(query, params)
        if "select id::text from documents" in query:
            self._fetchone = ("document-1",)

    def fetchall(self):
        # Fix #2: токенайзер сохраняет '\n\n' между header и body — фикстура должна
        # отдавать тот же формат, иначе ingest решит что контент изменился и
        # удалит-перевставит chunks вместо backfill embeddings.
        if "select content from document_chunks" in self.last_query:
            return [("# Policy\n\nТекст политики отпусков.",)]
        return [("chunk-1", "# Policy\n\nТекст политики отпусков.")]


class ExistingChangedCursor(FakeCursor):
    def execute(self, query, params=None):
        super().execute(query, params)
        if "select id::text from documents" in query:
            self._fetchone = ("document-1",)

    def fetchall(self):
        if "select content from document_chunks" in self.last_query:
            return [("Старый текст политики.",)]
        return []


def test_ingestion_writes_chunks_with_mistral_embeddings(monkeypatch):
    Path(".pytest_cache").mkdir(exist_ok=True)
    with TemporaryDirectory(dir=Path(".pytest_cache")) as temp_dir:
        docs_path = Path(temp_dir) / "docs"
        docs_path.mkdir()
        (docs_path / "policy.md").write_text("# Policy\n\nТекст политики отпусков.", encoding="utf-8")
        inserted_count = _run_ingestion(monkeypatch, docs_path)

    assert inserted_count == 1


def test_ingestion_uses_manifest_file_list(monkeypatch):
    Path(".pytest_cache").mkdir(exist_ok=True)
    with TemporaryDirectory(dir=Path(".pytest_cache")) as temp_dir:
        root_path = Path(temp_dir)
        docs_path = root_path / "docs"
        docs_path.mkdir()
        (docs_path / "included.md").write_text("# Included\n\nНужный документ.", encoding="utf-8")
        (docs_path / "skipped.md").write_text("# Skipped\n\nЛишний документ.", encoding="utf-8")
        manifest_path = root_path / "manifest.txt"
        manifest_path.write_text("included.md\n", encoding="utf-8")
        cursor = FakeCursor()
        store = PostgresStore("postgresql://local/test")

        monkeypatch.setattr(store, "_connect", lambda: FakeConnection(cursor))

        inserted_count = store.ingest_documents(docs_path, FakeEmbeddingClient(), manifest_path=manifest_path)

    assert inserted_count == 1
    assert len(cursor.inserted_chunks) == 1
    assert cursor.inserted_chunks[0][2] == "# Included\n\nНужный документ."


def _run_ingestion(monkeypatch, docs_path: Path) -> int:
    cursor = FakeCursor()
    store = PostgresStore("postgresql://local/test")

    monkeypatch.setattr(store, "_connect", lambda: FakeConnection(cursor))

    inserted_count = store.ingest_documents(docs_path, FakeEmbeddingClient())

    assert cursor.inserted_chunks
    chunk_params = cursor.inserted_chunks[0]
    # Fix #2: token splitter сохраняет оригинальный whitespace (newlines),
    # а не сворачивает в " " как старый word-based " ".join(words).
    assert chunk_params[2] == "# Policy\n\nТекст политики отпусков."
    assert chunk_params[5].startswith("[0.1,")
    return inserted_count


def test_ingestion_backfills_missing_embeddings_for_existing_chunks(monkeypatch):
    Path(".pytest_cache").mkdir(exist_ok=True)
    with TemporaryDirectory(dir=Path(".pytest_cache")) as temp_dir:
        docs_path = Path(temp_dir) / "docs"
        docs_path.mkdir()
        (docs_path / "policy.md").write_text("# Policy\n\nТекст политики отпусков.", encoding="utf-8")
        cursor = BackfillCursor()
        store = PostgresStore("postgresql://local/test")

        monkeypatch.setattr(store, "_connect", lambda: FakeConnection(cursor))

        updated_count = store.ingest_documents(docs_path, FakeEmbeddingClient())

    assert updated_count == 1
    assert cursor.updated_chunks
    assert cursor.updated_chunks[0][0].startswith("[0.1,")
    assert cursor.updated_chunks[0][1] == "chunk-1"


def test_ingestion_replaces_chunks_when_existing_document_changes(monkeypatch):
    Path(".pytest_cache").mkdir(exist_ok=True)
    with TemporaryDirectory(dir=Path(".pytest_cache")) as temp_dir:
        docs_path = Path(temp_dir) / "docs"
        docs_path.mkdir()
        (docs_path / "policy.md").write_text("# Policy\n\nНовый текст политики.", encoding="utf-8")
        cursor = ExistingChangedCursor()
        store = PostgresStore("postgresql://local/test")

        monkeypatch.setattr(store, "_connect", lambda: FakeConnection(cursor))

        inserted_count = store.ingest_documents(docs_path, FakeEmbeddingClient())

    assert inserted_count == 1
    assert cursor.deleted_document_ids == ["document-1"]
    assert cursor.inserted_chunks
    assert cursor.inserted_chunks[0][2] == "# Policy\n\nНовый текст политики."
