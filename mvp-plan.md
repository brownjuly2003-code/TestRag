# TestRag MVP Plan

## Goal

Собрать рабочий MVP HR/legal RAG-ассистента: Telegram-вопрос, n8n workflow, hybrid search по Supabase `pgvector` + BM25, ответ через Mistral с источниками, логирование и оценка качества.

## Tasks

- [x] Создать стартовый каркас проекта: Docker Compose для n8n, Postgres/pgvector, RAG API. Verify: `docker compose config --quiet`.
- [x] Подготовить 3 демо-документа для локального корпуса. Verify: RAG API видит sample chunks через `/health`.
- [x] Подключить ingestion в Postgres: `TokenTextSplitter(chunk_size=500, chunk_overlap=50)`, Mistral embeddings, запись в `document_chunks`. Verify: в базе появились чанки с метаданными и embeddings.
- [x] Реализовать начальный hybrid retrieval endpoint для RAG API. Verify: unit-тест возвращает top-k chunks с BM25 score и итоговым score.
- [x] Добавить классификацию запроса и порог confidence. Verify: слабый запрос получает отказ, релевантный запрос проходит дальше.
- [x] Добавить ответ через Mistral с fallback на grounded extractive answer. Verify: каждый ответ содержит минимум один источник или отказ.
- [x] Добавить генерацию черновика по 1 шаблону через кодовое заполнение полей. Verify: на тестовых данных создается черновик без свободной генерации финального документа.
- [x] Собрать стартовый n8n workflow: Telegram, whitelist, вызов RAG API, кнопки оценки. Verify: workflow JSON парсится.
- [x] Добавить запись логов, оценок и очереди ревью в Postgres из API/n8n. Verify: плохая оценка появляется в `review_queue`.
- [x] Phase 10: Verification. Прогнать демо-сценарии HR, legal, low-confidence и template draft. Verify: результаты совпадают с MVP-критериями.

## Done When

- [ ] Telegram-бот отвечает только whitelist-пользователям.
- [x] Ответы по нормативным вопросам всегда содержат источники.
- [x] Низкая уверенность приводит к отказу, а не к выдуманному ответу.
- [x] Все запросы и оценки логируются.
- [x] Плохие ответы попадают в очередь ревью.
- [ ] MVP можно показать за 4-5 рабочих дней без покупки n8n Cloud.

## Notes

- n8n используется как оркестратор, RAG-логика остается в коде.
- Retrieval делается гибридным: vector search + BM25.
- LLM и embeddings: Mistral.
- Для тестового достаточно self-hosted n8n.
- Интеграция с платными правовыми системами остается за рамками MVP.
