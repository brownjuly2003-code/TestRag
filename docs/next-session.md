# Next Session

## Как начать следующую сессию

Скопируй в новый чат:

```text
Продолжаем проект D:\TestRag.

Контекст:
- Это MVP HR/legal RAG-ассистента по ТЗ из PDF.
- n8n нужен как self-hosted оркестратор, не покупаем n8n Cloud.
- RAG API: FastAPI, Mistral, hybrid retrieval = BM25 + pgvector.
- База: Postgres/pgvector через Docker Compose.
- Telegram bot: токен лежит только в локальном .env, его не выводить.
- Документация: README.md, mvp-plan.md, docs/demo-runbook.md, docs/legal-document-prompts.md.
- MVP-корпус включается безопасно через DOCS_PATH + DOCS_MANIFEST_PATH, чтобы не индексировать все 200 corpus-файлов случайно.

Что уже сделано:
- docker-compose.yml для n8n + Postgres/pgvector + rag-api.
- RAG API с /health, /ask, /feedback, /document/type-detection.
- BM25 retriever и confidence policy.
- sample docs в data/sample_docs и manifest shortlist в manifests/MVP_CORPUS_FILES.txt.
- SQL init schema в sql/init.sql.
- n8n workflow JSON в n8n/workflows/hr-legal-rag-workflow.json.
- n8n IF-маршрутизация исправлена и активный workflow переимпортирован: `Authorized?` true -> `Feedback?`, false -> `Send Denied`; `Feedback?` true -> `Send Feedback`, false -> `Ask RAG API`.
- ingestion в Postgres: chunks + Mistral embeddings + document_chunks.
- реальные логи request_logs, answer_feedback, review_queue.
- pytest: 15 тестов проходят.
- Текущий расширенный corpus health: `/health` -> `chunk_count=122`, `postgres_enabled=true`, `mistral_enabled=true`, `embeddings_enabled=true`.
- Opus handoff: исходные отчеты `opus_result_*.md`, следующий набор `opus_result_next_*.md`, новые независимые задачи в `opus_task.md` пишут только `opus_result_followup_*.md`.

Что нужно делать дальше:
1. Проверить, запущен ли Docker Desktop.
2. Для минимального demo оставить DOCS_PATH=/app/data/sample_docs; для MVP-корпуса поставить DOCS_PATH=/app/corpus и DOCS_MANIFEST_PATH=/app/manifests/MVP_CORPUS_FILES.txt.
3. Запустить docker compose up --build или пересоздать rag-api после смены DOCS_PATH.
4. Проверить live Telegram happy path для whitelist-пользователя: `привет` не должен возвращать пустую n8n-приписку, доменный вопрос должен вызвать `/ask`.
5. Проверить feedback-кнопки: good/bad пишутся в answer_feedback, bad попадает в review_queue.
6. Прогнать docs/demo-runbook.md end-to-end.

Перед работой:
- Не выводить .env и секреты.
- После изменений запускать python -m pytest.
- Если трогаешь Docker, проверять docker compose config --quiet.
```

## Минимальные команды

```powershell
cd D:\TestRag
python -m pytest -p no:schemathesis
docker compose config --quiet
docker compose up --build
```

Если `docker compose up --build` падает на подключении к `dockerDesktopLinuxEngine`, сначала запустить Docker Desktop.
