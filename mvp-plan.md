# TestRag MVP Plan

## Goal

Собрать рабочий MVP HR/legal RAG-ассистента для авиагрузовой компании: Telegram-вопрос, n8n workflow, hybrid search по Postgres/pgvector + BM25, ответ через Mistral с источниками, логирование, оценка качества, drill-down feedback с категорией.

## Current Status

Updated: 2026-05-17 (HEAD `909bd42` после Sprint 1+2).

- [x] Docker Compose поднят: `postgres`, `rag-api`, `n8n`, `cloudflared`.
- [x] n8n workflow активирован, публичный webhook через cloudflare tunnel (trycloudflare).
- [x] Локальный Telegram whitelist для `432751211`.
- [x] RAG API: `chunk_count=207`, `documents=48`, postgres/mistral/embeddings enabled.
- [x] Postgres tables: documents, document_chunks, request_logs, answer_feedback (+category +free_text +chunk_ids после M7), review_queue.
- [x] **pytest 68/68** (`python -m pytest -p no:schemathesis`).
- [x] Workflow 24 узла активный (TelegramTrigger → Whitelist → Authorized? → Feedback? → Bad Clarify? → Direct Reply? → History? → Docs? → Send Typing → Ask RAG API → Format Answer → Last Part? → Send Answer / Send Answer Part).
- [x] Aviation profile pass на 200 corpus-файлов. MVP-44 подборка ingested.
- [x] Live TG smoke: controlled-zone Q ответил с HTML, 2 кнопки, drill-down работает.
- [x] Split до 4000 chars подтверждён через `.tmp/smoke_split.py`: 2 parts (3895+674) в реальный чат, keyboard только на last.

## Sprint 1 — must-have UX polish ✅ DONE (2026-05-17)

Закрыто за день. Все 6 пунктов в `docs/research/SYNTHESIS.md` `Sprint 1 must-have`:

- [x] Заменить «Good/Bad» лейблы на «👍 Полезно / 👎 Неточно». Удалить кнопку «📋 Нужны источники» (anti-pattern).
- [x] `sendChatAction('typing')` через HTTP-узел Bot API перед Ask RAG API.
- [x] `parse_mode='HTML'` на Send Answer/Direct Reply/Feedback Ack/Denied. Format Answer переписан с HTML-escape + filenames в `<code>`.
- [x] **MD→HTML конверсия** в Format Answer (`**X**`→`<b>X</b>`, `` `X` ``→`<code>X</code>`, `- ` → `• `) — фикс после первого TG-смока, см. `docs/known-issues.md` issue 3.
- [x] Убрать «Confidence: N» → «Найдено N релевантных документ(а/ов)» с русским склонением.
- [x] Drill-down на 👎: `feedback:bad:` → `feedback_bad_clarify` → новый узел Edit Reply Markup (HTTP) подменяет клавиатуру исходного сообщения на 3 reason-кнопки. Reason-клик пишет `category` в `answer_feedback`.

**Hotfixes Sprint 1**:
- [x] Ask RAG API брал `text/user_id` из `$json` (Send Typing HTTP затирал) → переписан на `$node['Whitelist'].json.*` + regression test. См. `docs/known-issues.md` issue 4.

## Sprint 2 — UX uplift ✅ DONE (2026-05-17)

Из `docs/research/SYNTHESIS.md` Sprint 2 nice-to-have. Закрыто 4 из 5, N1 отложен в Sprint 3.

- [x] Команды `/help` (HTML список), `/clear` (про stateless), `/history` (последние 5 из request_logs с русским склонением), `/docs` (8 категорий, 48 docs).
- [x] M7 schema: `answer_feedback` +`category` text, +`free_text` text nullable, +`chunk_ids` jsonb (auto-pulled из `request_logs.sources` по `request_log_id`). Миграция ALTER TABLE применена.
- [x] N5 endpoint `GET /docs/summary`: группирует documents по prefix file_name (01_hr_pol/02_hr_tpl/03_legal_con/04_legal_cla/05_tlog/06_comp/07_faq/other) с подсчётом docs.
- [ ] **N1 Follow-up question buttons** — DEFERRED to Sprint 3 (см. ниже).
- [x] **TG 4096 char split** (вне SYNTHESIS, но критично): Format Answer split по `\n\n` paragraph / предложению / hard chunk. `balanceTags()` дозакрывает разорванные `<b>/<code>`. Workflow `Last Part? If` → `Send Answer` (keyboard) / `Send Answer Part` (без keyboard). См. `docs/known-issues.md` issues 5+6.

## Sprint 3 — production polish (NEXT — 1-2 дня)

### N1 Follow-up question buttons (priority 1)

Цель: после ответа на вопрос юзер видит 2 кнопки «уточняющий вопрос», клик отправляет новый Q в RAG API.

План (детально в `docs/next-session.md`):
- **rag-api**: новый endpoint `GET /followup?request_log_id=X&idx=Y` → возвращает crafted question из `request_logs.sources[Y].section` или `.file`.
- **storage**: `get_request_source(rl_id, idx) -> dict | None`.
- **Whitelist**: parse `callback_data='followup:<idx>:<rl_uuid>'` (47 байт, fits в TG 64-byte лимит) → `event_type='followup_request'`.
- **Workflow**: новый `Followup? If` после `Docs? false` → `Resolve Follow-up` HTTP-узел (GET /followup) → `Set Question` Code-узел трансформирует `{question: "..."}` в shape, ожидаемый Send Typing/Ask RAG → продолжает по существующему RAG-пути.
- **Send Answer refactor**: с Telegram-node на HTTP-node (POST sendMessage), чтобы inline_keyboard был dynamic — добавить 2 follow-up кнопок на основе `sources[0..1].section` + 2 feedback кнопок.
- **Format Answer**: на последнем item добавить `follow_ups: [{label, callback}]` array.
- **Тесты**: parse followup callback, /followup endpoint, workflow routing, dynamic inline keyboard.

Сложность: ~6-8 новых узлов в workflow, ~30 LOC в storage+main, ~5-7 новых тестов.

### N3 Human handover (priority 2)

Цель: при `feedback:bad_human` → запись в review_queue с last 5 сообщений + confirmation user'у.

- [x] `feedback:bad_human` уже пишет `category='human'` в answer_feedback (через Sprint 1 drill-down).
- [ ] Добавить column `review_queue.context` jsonb для last 5 messages.
- [ ] Endpoint `/feedback` при `category='human'` дополнительно подтягивает `recent_requests(telegram_user_id, limit=5)` и пишет в `review_queue.context`.
- [ ] Workflow Format Feedback при `category='human'` отправляет «Ваш запрос направлен HR/Legal на ручную обработку, ответят в течение N рабочих дней».

### N4 Conversation threading (priority 3)

Цель: reply-to-message подмешивает prev 3 QA в retrieval query.

- [ ] Whitelist: detect `$json.callback_query.message.reply_to_message` / `$json.message.reply_to_message`.
- [ ] При наличии reply_to: extract `thread_id` (parent message_id) + lookup prev requests via `get_thread_history(thread_id)`.
- [ ] /ask: accept optional `prev_context: list[str]` параметр → prepend в retrieval query.
- [ ] DB: новая таблица `message_threads(message_id, request_log_id, parent_message_id)`.

### N2 Quick-actions (priority 4)

- [ ] «Уточнить» — rerun с top_k=10 (вместо 5).
- [ ] «Развернуть» — full chunk content вместо snippet.

### Sprint 4 — retrieval polish (low-priority но необходим для production)

- [ ] **Retrieval polluted** (см. `docs/known-issues.md` issue 1 + `docs/findings/2026-05-17-retrieval-aviation-pollution.md`): controlled-zone Q даёт top=HR-шаблоны. Aviation pass раскидал aviation-tokens по всем файлам. Fix: re-profile aviation pass только для tlog/safety/comp файлов.

## Anti-patterns (явно НЕ делаем)

- ❌ Confidence как сырое `0.73` в UI (заменили на «Найдено N»).
- ❌ MarkdownV2 в динамическом контенте (HTML стабильнее, escape-friendly).
- ❌ Длинный disclaimer ДО ответа (одна строка после — OK).
- ❌ Sources только по кнопке (всегда inline).
- ❌ Truncate длинного ответа (вместо split с пометкой «часть N/M»).
- ❌ Voice/audio messages; multi-language switch; RAGAs eval dashboard.

## Done When

- [x] Telegram-бот отвечает только whitelist-пользователям.
- [x] Ответы по нормативным вопросам всегда содержат источники.
- [x] Низкая уверенность приводит к отказу, а не к выдуманному ответу.
- [x] Все запросы и оценки логируются.
- [x] Плохие ответы попадают в очередь ревью.
- [x] Feedback drill-down: 👎 → 3 категории → answer_feedback.category.
- [x] HTML рендер ответа без `**markdown**`-артефактов.
- [x] Длинные ответы > 4096 chars не теряются (split на части).
- [x] Команды /help, /history, /docs работают.
- [ ] N1 Follow-up question buttons (Sprint 3).
- [ ] N3 Human handover с context (Sprint 3).
- [ ] Retrieval polish: top-source соответствует домену вопроса (Sprint 4).
- [ ] MVP можно показать без покупки n8n Cloud по `docs/demo-runbook.md` (зависит от cloudflare named tunnel или paid n8n).

## Known Issues

Полный список в `docs/known-issues.md`. Главные:

| # | issue | severity | fix |
|---|---|---|---|
| 1 | Retrieval polluted после aviation pass | high (prod) / low (demo) | Sprint 4 |
| 2 | TG webhook secret in-memory | low (только тестирование) | n/a (n8n upstream) |
| 7 | Mistral free tier 429 | medium (prod) | paid tier для prod |
| 10 | Cloudflare tunnel эфемерные URLs | medium (demo) | named tunnel или real domain |

## Notes

- n8n используется как оркестратор, RAG-логика остается в коде (rag-api/app).
- Retrieval гибридный: pgvector + BM25, оба BM25 и vector scores combined с весами в HybridRetriever.
- LLM и embeddings: Mistral. Free tier хватает для demo, для prod нужен paid tier (issue 7).
- Workflow 24 узла, активно `executionOrder=v1`.
- TG callback_data 64-byte лимит влияет на N1 design (см. Sprint 3).
- После любого изменения rag-api Python: `docker compose build rag-api && docker compose up -d --force-recreate rag-api` (см. issue 9).
- После изменения workflow JSON: re-import через CLI с `MSYS_NO_PATHCONV=1` (issue 8).
