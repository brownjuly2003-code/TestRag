from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import psycopg
import yaml
from psycopg.types.json import Jsonb

from .rag import DocumentChunk, split_text


logger = logging.getLogger(__name__)

_DEFAULT_DOC_DATE = "2026-05-15"


def _consensus_dim(embeddings: list[list[float] | None]) -> int:
    """Most-common non-None embedding length. Возвращает 0 если эмбеддинги
    пустые/None — тогда mismatch-warn просто не активируется."""
    lens = [len(e) for e in embeddings if e]
    if not lens:
        return 0
    return max(set(lens), key=lens.count)


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Fix #1 step 4: разбираем YAML frontmatter из corpus/*.md.

    Frontmatter формат:

        ---
        source_url: https://...
        effective_date: 2024-01-01
        document_type: federal_law
        ---
        # Заголовок

    Возвращает (meta, body). Если frontmatter нет/невалидный — meta={} и
    body=text как есть.
    """
    if not text.startswith("---"):
        return {}, text
    parts = text.split("\n---", 1)
    if len(parts) != 2:
        return {}, text
    raw = parts[0][3:].lstrip("\n")
    body = parts[1].lstrip("\n")
    try:
        data = yaml.safe_load(raw) or {}
    except yaml.YAMLError:
        return {}, text
    if not isinstance(data, dict):
        return {}, text
    return data, body


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
                raw_text = file_path.read_text(encoding="utf-8")
                # Fix #1 step 4: frontmatter parsing — source_url / effective_date /
                # document_type / version подставляем из YAML заголовка, не из
                # хардкода "2026-05-15".
                frontmatter, text = _parse_frontmatter(raw_text)
                section = _detect_section(text)
                chunks = split_text(text)
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

                doc_date = str(
                    frontmatter.get("effective_date")
                    or frontmatter.get("date")
                    or _DEFAULT_DOC_DATE
                )
                source_url = str(frontmatter.get("source_url") or "")
                document_type = str(frontmatter.get("document_type") or "demo")
                version = str(frontmatter.get("version") or "v1")

                embeddings = embedding_client.embed_texts(chunks) if chunks else []
                expected_dim = _consensus_dim(embeddings)
                for index, chunk_text in enumerate(chunks):
                    metadata = {
                        "file": file_path.name,
                        "section": section,
                        "date": doc_date,
                        "source_url": source_url,
                        "document_type": document_type,
                        "version": version,
                    }
                    embedding = embeddings[index] if index < len(embeddings) else None
                    # Sprint 8 #2 (codex-audit#6.2): silent dim mismatch отбрасывает
                    # vector score в zero на retrieval (cosine_similarity → 0). Здесь
                    # ловим расхождение на этапе ingestion, чтобы оператор увидел
                    # проблему до запроса. Mixed embedding models / partial vendor
                    # responses теперь явные в логах.
                    if embedding is not None and expected_dim and len(embedding) != expected_dim:
                        logger.warning(
                            "ingest.dim_mismatch file=%s chunk_idx=%d expected=%d got=%d "
                            "(possible mixed embedding model)",
                            file_path.name,
                            index,
                            expected_dim,
                            len(embedding),
                        )
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
                    d.document_date::text,
                    d.version,
                    d.effective_from::text,
                    d.effective_to::text,
                    d.status
                from document_chunks c
                join documents d on d.id = c.document_id
                where d.status <> 'superseded'
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
            metadata["version"] = row[9] or "v1"
            metadata["effective_from"] = row[10] or None
            metadata["effective_to"] = row[11] or None
            metadata["status"] = row[12] or "active"
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
        latency_ms: int | None = None,
        llm_model: str | None = None,
        prompt_tokens: int | None = None,
        completion_tokens: int | None = None,
    ) -> str | None:
        if not self.enabled:
            return None

        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                insert into request_logs
                    (telegram_user_id, question, request_type, confidence, refused, answer, sources,
                     latency_ms, llm_model, prompt_tokens, completion_tokens)
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                    latency_ms,
                    llm_model,
                    prompt_tokens,
                    completion_tokens,
                ),
            )
            row = cursor.fetchone()
        return row[0] if row else None

    def metrics(self, window_hours: int = 168) -> dict[str, Any]:
        """Returns aggregated /ask metrics over last `window_hours` (default 7 days)."""
        if not self.enabled:
            return {
                "window_hours": window_hours,
                "total_requests": 0,
                "refusal_rate": 0.0,
                "avg_latency_ms": None,
                "avg_confidence": None,
                "avg_prompt_tokens": None,
                "avg_completion_tokens": None,
                "bad_feedback_rate": 0.0,
            }
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                select
                    count(*),
                    avg(case when refused then 1.0 else 0.0 end),
                    avg(latency_ms),
                    avg(confidence),
                    avg(prompt_tokens),
                    avg(completion_tokens)
                from request_logs
                where created_at >= now() - make_interval(hours => %s)
                """,
                (window_hours,),
            )
            row = cursor.fetchone() or (0, 0.0, None, None, None, None)
            cursor.execute(
                """
                select
                    sum(case when rating = 'bad' then 1 else 0 end)::float
                        / nullif(count(*), 0)
                from answer_feedback
                where created_at >= now() - make_interval(hours => %s)
                """,
                (window_hours,),
            )
            bad_row = cursor.fetchone()
            bad_rate = float(bad_row[0]) if bad_row and bad_row[0] is not None else 0.0
        return {
            "window_hours": window_hours,
            "total_requests": int(row[0] or 0),
            "refusal_rate": float(row[1] or 0.0),
            "avg_latency_ms": float(row[2]) if row[2] is not None else None,
            "avg_confidence": float(row[3]) if row[3] is not None else None,
            "avg_prompt_tokens": float(row[4]) if row[4] is not None else None,
            "avg_completion_tokens": float(row[5]) if row[5] is not None else None,
            "bad_feedback_rate": bad_rate,
        }

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
                with categorized as (
                    select distinct
                        d.id,
                        d.file_name,
                        case
                            when file_name ~ '^[0-9]+_hr_pol' then '01_hr_pol'
                            when file_name ~ '^[0-9]+_hr_(tmp|tpl)' then '02_hr_tpl'
                            when file_name ~ '^[0-9]+_legal_con' then '03_legal_con'
                            when file_name ~ '^[0-9]+_legal_cla' then '04_legal_cla'
                            when file_name ~ '^[0-9]+_tlog' then '05_tlog'
                            when file_name ~ '^[0-9]+_comp' then '06_comp'
                            when file_name ~ '^[0-9]+_faq' then '07_faq'
                            else 'other'
                        end as category
                    from documents d
                    join document_chunks c on c.document_id = d.id
                ),
                top_samples as (
                    select category, array_agg(file_name order by file_name) as files
                    from (
                        select category, file_name,
                            row_number() over (partition by category order by file_name) as rn
                        from categorized
                    ) ranked
                    where rn <= 2
                    group by category
                )
                select
                    c.category,
                    count(*) as doc_count,
                    coalesce(s.files, '{}'::text[]) as sample_files
                from categorized c
                left join top_samples s on s.category = c.category
                group by c.category, s.files
                order by c.category
                """
            )
            rows = cursor.fetchall()
        return [
            {
                "category": row[0],
                "doc_count": int(row[1]),
                "sample_files": list(row[2] or []),
            }
            for row in rows
        ]

    def get_request_source(self, request_log_id: str, idx: int) -> dict[str, Any] | None:
        if not self.enabled or not request_log_id or idx < 0:
            return None
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "select sources from request_logs where id::text = %s",
                    (request_log_id,),
                )
                row = cursor.fetchone()
        except psycopg.errors.InvalidTextRepresentation:
            return None
        if not row or not row[0]:
            return None
        sources = row[0]
        if not isinstance(sources, list) or idx >= len(sources):
            return None
        entry = sources[idx]
        return entry if isinstance(entry, dict) else None

    def get_request_question(self, request_log_id: str) -> str | None:
        """Sprint 6 #6 (N2 Quick-actions): забрать оригинальный вопрос по request_log_id
        для /clarify rerun."""
        if not self.enabled or not request_log_id:
            return None
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "select question from request_logs where id::text = %s",
                    (request_log_id,),
                )
                row = cursor.fetchone()
        except psycopg.errors.InvalidTextRepresentation:
            return None
        if not row:
            return None
        question = row[0]
        return question if isinstance(question, str) and question.strip() else None

    def enqueue_review(
        self,
        request_log_id: str | None,
        reason: str,
        context: list[dict[str, Any]] | None = None,
    ) -> str | None:
        if not self.enabled or not request_log_id:
            return None

        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                insert into review_queue (request_log_id, reason, context)
                values (%s, %s, %s)
                returning id::text
                """,
                (request_log_id, reason, Jsonb(context or [])),
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
