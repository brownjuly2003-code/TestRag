from __future__ import annotations

from pathlib import Path
from typing import Any

import psycopg
from psycopg.types.json import Jsonb

from .rag import DocumentChunk


class PostgresStore:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    @property
    def enabled(self) -> bool:
        return bool(self.database_url)

    def _connect(self):
        return psycopg.connect(self.database_url, autocommit=True)

    def ingest_documents(self, docs_path: Path, embedding_client: Any, manifest_path: Path | None = None) -> int:
        if not self.enabled or not docs_path.exists():
            return 0

        inserted_count = 0
        with self._connect() as conn:
            cursor = conn.cursor()
            for file_path in _iter_document_files(docs_path, manifest_path):
                document_id = self._get_or_create_document(cursor, file_path)
                text = file_path.read_text(encoding="utf-8")
                section = _detect_section(text)
                chunks = _split_text(text)
                cursor.execute(
                    "select content from document_chunks where document_id = %s order by chunk_index",
                    (document_id,),
                )
                existing_chunks = [row[0] for row in cursor.fetchall()]
                if existing_chunks == chunks:
                    inserted_count += self._backfill_missing_embeddings(cursor, document_id, embedding_client)
                    continue
                if existing_chunks:
                    cursor.execute("delete from document_chunks where document_id = %s", (document_id,))

                embeddings = embedding_client.embed_texts(chunks) if chunks else []
                for index, chunk_text in enumerate(chunks):
                    metadata = {
                        "file": file_path.name,
                        "section": section,
                        "date": "2026-05-15",
                        "source_url": "",
                        "document_type": "demo",
                    }
                    embedding = embeddings[index] if index < len(embeddings) else None
                    cursor.execute(
                        """
                        insert into document_chunks
                            (document_id, chunk_index, content, section, metadata, embedding)
                        values (%s, %s, %s, %s, %s, %s::vector)
                        """,
                        (
                            document_id,
                            index,
                            chunk_text,
                            section,
                            Jsonb(metadata),
                            _format_embedding(embedding),
                        ),
                    )
                    inserted_count += 1
        return inserted_count

    def load_chunks(self) -> list[DocumentChunk]:
        if not self.enabled:
            return []

        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                select
                    c.id::text,
                    c.content,
                    c.section,
                    c.metadata,
                    c.embedding::text,
                    d.file_name,
                    d.source_url,
                    d.document_type,
                    d.document_date::text
                from document_chunks c
                join documents d on d.id = c.document_id
                order by d.file_name, c.chunk_index
                """
            )
            rows = cursor.fetchall()

        chunks: list[DocumentChunk] = []
        for row in rows:
            metadata = dict(row[3] or {})
            metadata.setdefault("file", row[5])
            metadata.setdefault("section", row[2])
            metadata.setdefault("source_url", row[6] or "")
            metadata.setdefault("document_type", row[7] or "")
            metadata.setdefault("date", row[8] or "")
            chunks.append(
                DocumentChunk(
                    chunk_id=row[0],
                    content=row[1],
                    metadata=metadata,
                    embedding=_parse_embedding(row[4]),
                )
            )
        return chunks

    def log_request(
        self,
        telegram_user_id: str | None,
        question: str,
        request_type: str,
        confidence: float,
        refused: bool,
        answer: str,
        sources: list[dict[str, Any]],
    ) -> str | None:
        if not self.enabled:
            return None

        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                insert into request_logs
                    (telegram_user_id, question, request_type, confidence, refused, answer, sources)
                values (%s, %s, %s, %s, %s, %s, %s)
                returning id::text
                """,
                (
                    telegram_user_id,
                    question,
                    request_type,
                    confidence,
                    refused,
                    answer,
                    Jsonb(sources),
                ),
            )
            row = cursor.fetchone()
        return row[0] if row else None

    def log_feedback(
        self,
        request_log_id: str | None,
        telegram_user_id: str | None,
        rating: str,
        comment: str | None,
        category: str | None = None,
        free_text: str | None = None,
    ) -> str | None:
        if not self.enabled:
            return None

        with self._connect() as conn:
            cursor = conn.cursor()
            chunk_ids: list[str] = []
            if request_log_id:
                cursor.execute(
                    "select sources from request_logs where id = %s",
                    (request_log_id,),
                )
                row = cursor.fetchone()
                if row and row[0]:
                    chunk_ids = [s.get("chunk_id") for s in row[0] if s.get("chunk_id")]
            cursor.execute(
                """
                insert into answer_feedback
                    (request_log_id, telegram_user_id, rating, comment, category, free_text, chunk_ids)
                values (%s, %s, %s, %s, %s, %s, %s)
                returning id::text
                """,
                (
                    request_log_id,
                    telegram_user_id,
                    rating,
                    comment,
                    category,
                    free_text,
                    Jsonb(chunk_ids),
                ),
            )
            row = cursor.fetchone()
        return row[0] if row else None

    def recent_requests(self, telegram_user_id: str, limit: int = 5) -> list[dict[str, Any]]:
        if not self.enabled:
            return []
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                select id::text, question, answer, confidence, refused, created_at
                from request_logs
                where telegram_user_id = %s
                order by created_at desc
                limit %s
                """,
                (telegram_user_id, limit),
            )
            rows = cursor.fetchall()
        return [
            {
                "id": row[0],
                "question": row[1],
                "answer": row[2],
                "confidence": float(row[3]) if row[3] is not None else None,
                "refused": row[4],
                "created_at": row[5].isoformat() if row[5] else None,
            }
            for row in rows
        ]

    def corpus_summary(self) -> list[dict[str, Any]]:
        if not self.enabled:
            return []
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                select
                    case
                        when file_name ~ '^[0-9]+_hr_pol' then '01_hr_pol'
                        when file_name ~ '^[0-9]+_hr_(tmp|tpl)' then '02_hr_tpl'
                        when file_name ~ '^[0-9]+_legal_con' then '03_legal_con'
                        when file_name ~ '^[0-9]+_legal_cla' then '04_legal_cla'
                        when file_name ~ '^[0-9]+_tlog' then '05_tlog'
                        when file_name ~ '^[0-9]+_comp' then '06_comp'
                        when file_name ~ '^[0-9]+_faq' then '07_faq'
                        else 'other'
                    end as category,
                    count(distinct d.id) as doc_count
                from documents d
                join document_chunks c on c.document_id = d.id
                group by 1
                order by 1
                """
            )
            rows = cursor.fetchall()
        return [{"category": row[0], "doc_count": int(row[1])} for row in rows]

    def enqueue_review(self, request_log_id: str | None, reason: str) -> str | None:
        if not self.enabled or not request_log_id:
            return None

        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                insert into review_queue (request_log_id, reason)
                values (%s, %s)
                returning id::text
                """,
                (request_log_id, reason),
            )
            row = cursor.fetchone()
        return row[0] if row else None

    def _get_or_create_document(self, cursor: Any, file_path: Path) -> str:
        cursor.execute(
            "select id::text from documents where file_name = %s order by created_at desc limit 1",
            (file_path.name,),
        )
        row = cursor.fetchone()
        if row:
            return row[0]

        cursor.execute(
            """
            insert into documents (file_name, document_type, document_date)
            values (%s, %s, %s)
            returning id::text
            """,
            (file_path.name, "demo", "2026-05-15"),
        )
        created = cursor.fetchone()
        return created[0]

    def _backfill_missing_embeddings(self, cursor: Any, document_id: str, embedding_client: Any) -> int:
        if not getattr(embedding_client, "enabled", True):
            return 0

        cursor.execute(
            """
            select id::text, content
            from document_chunks
            where document_id = %s and embedding is null
            order by chunk_index
            """,
            (document_id,),
        )
        rows = cursor.fetchall()
        if not rows:
            return 0

        embeddings = embedding_client.embed_texts([row[1] for row in rows])
        updated_count = 0
        for index, row in enumerate(rows):
            embedding = embeddings[index] if index < len(embeddings) else None
            if not embedding:
                continue
            cursor.execute(
                "update document_chunks set embedding = %s::vector where id = %s",
                (_format_embedding(embedding), row[0]),
            )
            updated_count += 1
        return updated_count


def _split_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[str]:
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = max(0, end - chunk_overlap)
    return chunks


def _detect_section(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("#"):
            return line.strip("# ").strip()
    return None


def _iter_document_files(docs_path: Path, manifest_path: Path | None = None) -> list[Path]:
    if not manifest_path:
        return sorted(docs_path.glob("*.md"))
    if not manifest_path.exists():
        return []

    root_path = docs_path.resolve()
    files = []
    seen = set()
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        entry = line.strip()
        if not entry or entry.startswith("#"):
            continue
        file_path = (root_path / entry).resolve()
        if file_path in seen:
            continue
        if file_path.suffix.lower() != ".md" or not file_path.is_file():
            continue
        if not file_path.is_relative_to(root_path):
            continue
        files.append(file_path)
        seen.add(file_path)
    return files


def _format_embedding(embedding: list[float] | None) -> str | None:
    if not embedding:
        return None
    return "[" + ",".join(str(value) for value in embedding) + "]"


def _parse_embedding(value: str | None) -> list[float] | None:
    if not value:
        return None
    return [float(item) for item in value.strip("[]").split(",") if item]
