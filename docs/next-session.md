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

Что уже сделано:
- docker-compose.yml для n8n + Postgres/pgvector + rag-api.
- RAG API с /health, /ask, /feedback.
- BM25 retriever и confidence policy.
- sample docs в data/sample_docs.
- SQL init schema в sql/init.sql.
- n8n workflow JSON в n8n/workflows/hr-legal-rag-workflow.json.
- pytest: 3 теста проходили.

Что нужно делать дальше:
1. Проверить, запущен ли Docker Desktop.
2. Запустить docker compose up --build.
3. Подключить ingestion в Postgres: chunks + Mistral embeddings + document_chunks.
4. Подключить реальные логи request_logs, answer_feedback, review_queue.
5. Добавить endpoint для document draft/type detection по docs/legal-document-prompts.md.
6. Настроить n8n Telegram credentials и tunnel для live-demo.

Перед работой:
- Не выводить .env и секреты.
- После изменений запускать python -m pytest.
- Если трогаешь Docker, проверять docker compose config --quiet.
```

## Минимальные команды

```powershell
cd D:\TestRag
python -m pytest
docker compose config --quiet
docker compose up --build
```

Если `docker compose up --build` падает на подключении к `dockerDesktopLinuxEngine`, сначала запустить Docker Desktop.
