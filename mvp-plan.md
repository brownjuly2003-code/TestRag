# TestRag MVP Plan

## Goal

Собрать рабочий MVP HR/legal RAG-ассистента: Telegram-вопрос, n8n workflow, hybrid search по Postgres/pgvector + BM25, ответ через Mistral с источниками, логирование и оценка качества.

## Current Status

Updated: 2026-05-17.

- [x] Docker Compose поднят: `postgres`, `rag-api`, `n8n`.
- [x] n8n workflow активирован, публичный webhook отвечает без ошибок.
- [x] n8n routing bug исправлен: whitelist true больше не ведет в `Send Denied`, обычные вопросы ведут в `Ask RAG API`, feedback ведет в `Send Feedback`.
- [x] Локальный Telegram whitelist настроен для `432751211`.
- [x] RAG API работает с Postgres/pgvector и Mistral: `/health` возвращает `postgres_enabled=true`, `mistral_enabled=true`, `embeddings_enabled=true`, `chunk_count=122`.
- [x] В Postgres есть рабочие данные: `documents=42`, `document_chunks=122`; `request_logs`, `answer_feedback` и `review_queue` заполняются.
- [x] Тесты API проходят: `python -m pytest -p no:schemathesis` -> `15 passed`.

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

## Next Tasks

- [ ] Проверить live Telegram happy path после настройки whitelist. Verify: сообщение от `432751211` проходит n8n, вызывает `/ask` и возвращает ответ в Telegram.
- [ ] Проверить live feedback path из Telegram-кнопок. Verify: `answer_feedback` увеличивается, bad feedback добавляет запись в `review_queue`.
- [x] Исправить n8n IF-ветки после симптома "бот отвечает только n8n attribution". Verify: active workflow в БД показывает `Authorized? true -> Feedback?`, `Authorized? false -> Send Denied`, `Feedback? true -> Send Feedback`, `Feedback? false -> Ask RAG API`; n8n пересоздан.
- [x] Отобрать MVP-корпус из `corpus/`. Verify: список файлов зафиксирован в `manifests/MVP_CORPUS_FILES.txt`, лишние документы не индексируются при включенном manifest.
- [x] Включить выбранный корпус в локальном `.env`: `DOCS_PATH=/app/corpus`, `DOCS_MANIFEST_PATH=/app/manifests/MVP_CORPUS_FILES.txt`, затем пересоздать `rag-api`. Verify: `/health` показывает `chunk_count=122`, а `document_chunks` содержит расширенный корпус с метаданными.
- [ ] Прогнать demo runbook end-to-end. Verify: HR-вопрос, legal-вопрос, low-confidence refusal и document draft проходят по ожидаемому сценарию.
- [x] Синхронизировать документацию по терминам `Postgres/pgvector` и `Supabase`. Verify: README и runbook одинаково описывают локальный MVP и возможный production target.
- [x] Aviation profile pass: перепрофилировать 200 corpus-файлов под авиагрузовую компанию + расширить MVP подборку до 44. Verify: aviation coverage 100%, golden Q 10/10 PASSED через /ask, top-source 01_hr_pol_safety.md для controlled zone Q.
- [x] TG E2E smoke: «привет» direct-reply OK, aviation Q «controlled zone» полный RAG-путь OK через @AIagentJu_bot.
- [x] Запросить research у Kimi и Codex по best practices RAG bot UX (HR/legal). Verify: оба независимых прохода сохранены в `docs/research/`, синтез в `docs/research/SYNTHESIS.md`.

## Bot UX Roadmap (по research-синтезу 2026-05-17)

Полная приоритизация и обоснование в `docs/research/SYNTHESIS.md`. Sprint-планы ниже — выдержка.

### Sprint 1 — must-have polish (0.5–1 день)

- [x] Заменить «Good/Bad» лейблы на «👍 Полезно / 👎 Неточно / 📋 Нужны источники» + перенести `replyMarkup` из `additionalFields` в top-level params (n8n v1.2 schema). 2026-05-17.
- [x] **Удалить кнопку «📋 Нужны источники»** (анти-паттерн по обоим research-проходам: sources должны быть всегда inline). Оставить 2 кнопки. 2026-05-17.
- [x] Добавить `sendChatAction('typing')` в n8n workflow перед `Ask RAG API` (HTTP-узел через Bot API). 2026-05-17.
- [x] Перейти на `parse_mode='HTML'` в Send Answer/Direct Reply/Feedback Ack/Denied; Format Answer переписан с HTML-escape, filenames в `<code>`. 2026-05-17.
- [x] Убрать вывод «Confidence: N» в UI. Заменить на «Найдено N релевантных документ(а/ов)» с русским склонением. 2026-05-17.
- [x] При 👎 → `event_type=feedback_bad_clarify` + `Edit Reply Markup` HTTP-узел подменяет клавиатуру на 3 reason-кнопки (Неточно/Устарело/Нужен человек). Reason-клик пишет `comment=category:<reason>` в `answer_feedback`. 2026-05-17.

### Sprint 2 — UX uplift (1–2 дня)

- [ ] Команды `/help`, `/clear`, `/history` (последние 5 запросов юзера из `request_logs`).
- [ ] Расширить `answer_feedback`: добавить `chunk_ids` (jsonb array), `category` (enum), `free_text` (nullable). Привязка feedback к ретривлу.
- [ ] Follow-up question buttons: 2 вопроса на основе top-3 chunks (template-based или короткий Mistral-вызов).
- [ ] `/docs` — список разделов корпуса (unique categories из frontmatter).

### Sprint 3 — production polish (1–2 дня)

- [ ] Human handover: «🧑‍💼 Связать с HR/Legal» при низкой conf или категории «нужен человек» → запись в `review_queue` с последними 5 сообщениями.
- [ ] Conversation threading: хранить `thread_id` в n8n, на reply-to-message подмешивать prev 3 QA в retrieval query.
- [ ] Quick-actions «Уточнить» (rerun с extended top_k) и «Развернуть» (full chunk вместо snippet).

### Anti-patterns (явно НЕ делаем)

- ❌ Confidence как сырое % в UI
- ❌ MarkdownV2 в динамическом контенте (HTML стабильнее для legal цитат)
- ❌ Длинный disclaimer ДО ответа
- ❌ Sources только по кнопке
- ❌ Voice/audio messages; multi-language switch; RAGAs eval dashboard

## Done When

- [ ] Telegram-бот отвечает только whitelist-пользователям в live-чате.
- [x] Ответы по нормативным вопросам всегда содержат источники.
- [x] Низкая уверенность приводит к отказу, а не к выдуманному ответу.
- [x] Все запросы и оценки логируются.
- [x] Плохие ответы попадают в очередь ревью.
- [ ] MVP можно показать без покупки n8n Cloud по `docs/demo-runbook.md`.

## Notes

- n8n используется как оркестратор, RAG-логика остается в коде.
- Retrieval делается гибридным: vector search + BM25.
- LLM и embeddings: Mistral.
- Для тестового достаточно self-hosted n8n.
- Интеграция с платными правовыми системами остается за рамками MVP.
- Перед demo-ready статусом нужен реальный Telegram-прогон после n8n routing fix, потому что локальные проверки подтверждают workflow/env/webhook/API, но не заменяют сообщение из клиента Telegram.
