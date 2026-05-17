# TestRag MVP Plan

## Goal

Собрать рабочий MVP HR/legal RAG-ассистента для авиагрузовой компании: Telegram-вопрос, n8n workflow, hybrid search по Postgres/pgvector + BM25, ответ через Mistral с источниками, логирование, оценка качества, drill-down feedback с категорией.

## Current Status

Updated: 2026-05-17 EOS (HEAD после Sprint 3 + ТЗ-критика sweep).

- [x] Docker Compose поднят: `postgres`, `rag-api`, `n8n`, `cloudflared`.
- [x] n8n workflow активирован, публичный webhook через cloudflare tunnel (trycloudflare).
- [x] Локальный Telegram whitelist для `432751211`.
- [x] RAG API: `chunk_count=207`, `documents=48`, postgres/mistral/embeddings enabled.
- [x] Postgres tables: documents (+version/effective_from/effective_to/status), document_chunks, request_logs (+latency_ms/llm_model/prompt_tokens/completion_tokens), answer_feedback (+category/free_text/chunk_ids), review_queue (+context jsonb).
- [x] **pytest 101/101** (`python -m pytest -p no:schemathesis`).
- [x] Workflow 28 узлов активный (Sprint 3 N1 +4 ветки: Followup? → Resolve Follow-up → Send Typing Followup → Ask RAG Followup).
- [x] Aviation profile pass на 200 corpus-файлов. MVP-44 подборка ingested.
- [x] Live TG E2E ✅ через `scripts/smoke_tg_e2e.py` (Telethon user account): N1 📎 click, N3 «🧑‍💼 → ACK», N4 reply_to=user_msg_id.
- [x] Split до 4000 chars подтверждён через `.tmp/smoke_split.py`.
- [x] ТЗ-критика 12 пунктов закрыта (см. `docs/research/2026-05-17-architecture-critique-tz.md`): 9 covered, 2 known-limitations (whitelist→SSO, external normative), 1 partial (structure-aware chunking).
- [x] Eval baseline: hit@1=0.22, MRR=0.28, refusal_acc=0.70, avg_latency=5700ms (`scripts/eval_retrieval.py --output .tmp/eval_baseline.json`).
- [x] /metrics endpoint: refusal_rate, avg_latency_ms, bad_feedback_rate за окно часов.
- [x] Section-keyword rerank в HybridRetriever (+10% per query-term match в section name, capped at +30%).

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

## Sprint 3 — production polish ✅ DONE (2026-05-17 EOS)

### N1 Follow-up question buttons ✅
- [x] `GET /followup?request_log_id=X&idx=Y` → crafted question; bogus UUID handled (psycopg `id::text = %s`).
- [x] `PostgresStore.get_request_source`.
- [x] Whitelist parses `followup:<idx>:<rl>` (47 chars).
- [x] Workflow 24→28 узлов (+Followup? / Resolve / Send Typing FU / Ask RAG FU).
- [x] Send Answer → HTTP sendMessage с dynamic `reply_markup: $json.inline_keyboard`.
- [x] Format Answer dedup сохраняет `_originalIdx` → callback на не-deduped позицию (pollution defence).
- [x] E2E live: `scripts/smoke_tg_e2e.py` через Telethon, нажатие 📎 → второй RAG-ответ.

### N3 Human handover ✅
- [x] `alter review_queue add column context jsonb default '[]'`.
- [x] `/feedback` при `category='human'` тянет `recent_requests(limit=5)` → `review_queue.context`.
- [x] Format Feedback узел: «Ваш запрос направлен HR/Legal на ручную обработку».
- [x] E2E live: bad → bad_human → ACK подтверждён.

### N4 Conversation threading ✅ (reply_to only)
- [x] Whitelist выставляет `user_message_id`.
- [x] Format Answer: первая часть → `reply_to_message_id`; остальные null.
- [x] Send Answer HTTP + Send Answer Part — `replyToMessageId`.
- [x] E2E live: reply_to=user_msg_id на основной ветке (followup ветка reply_to=None — minor known limitation).
- [ ] **Prev-N-QA в retrieval query** — отложено (риск сбить hybrid retrieval, нужен A/B по golden Q. См. backlog #6 в `docs/next-session.md`).

### ТЗ-критика 12 пунктов ✅ (2026-05-17 EOS)

Полная таблица в `docs/research/2026-05-17-architecture-critique-tz.md`. Закрыты:
- **#1 Retrieval contract**: `AskResponse.status` (answerable/unanswerable/needs_human_review), `effective_date_max`, `latency_ms`; `Source` пробрасывает `version/effective_from/effective_to/status`.
- **#3 Reranking**: section-keyword rerank в `HybridRetriever._section_boost` (+10% per query-term match, capped at +30%).
- **#5 Versioning**: `documents.version/effective_from/effective_to/status`; `load_chunks` фильтрует `superseded`.
- **#8 Eval pipeline**: `scripts/eval_retrieval.py` — Hit@1, Hit@5, MRR, refusal_accuracy, baseline сохранён.
- **#12 Observability**: `request_logs.latency_ms/llm_model/prompt_tokens/completion_tokens` + `GET /metrics?window_hours=N`.

Known limitations (out of MVP scope, документированы):
- **#4 Structure-aware chunking**: фиксированный 500/50 OK для 200 markdown.
- **#6 Whitelist→SSO/RLS**: TG whitelist для MVP. Production требует SSO + Postgres RLS.
- **#9 External normative**: corpus local, без live-обновления норм.

## Sprint 4 — retrieval polish (NEXT)

Цель: поднять Hit@1 ≥0.6, MRR ≥0.55 на golden Q (текущий baseline: 0.22 / 0.28).

- [ ] **Retrieval polluted fix** (`docs/findings/2026-05-17-retrieval-aviation-pollution.md`): re-profile aviation pass только для tlog/safety/comp файлов. HR-шаблоны откатить к pre-aviation версии. 3-5 часов.
- [ ] **Boost section weight** в HybridRetriever: текущий +10% per match → попробовать +20%, замерить через eval.
- [ ] **Document type filter в /ask**: optional `document_type: str` параметр → ограничивает retrieval по metadata.document_type.
- [ ] **Eval-driven gate**: добавить `pytest scripts/test_eval_regression.py` который читает `.tmp/eval_baseline.json` и упирается если MRR упал ниже baseline.

## Sprint 5 — production hardening (если потребуется)

- [ ] **N2 Quick-actions**: «Уточнить» (top_k=10 rerun), «Развернуть» (full chunk content).
- [ ] **Prev-N-QA в retrieval** (after Sprint 4 stability): ablation A/B на golden Q.
- [ ] **Structure-aware chunking**: split по markdown `##`/`###` headers вместо фиксированных 500 токенов.
- [ ] **SSO + RLS**: per-user role + Supabase-style row level security на document_chunks.
- [ ] **External normative ingestion**: один lawsource live-обновляемый (КонсультантПлюс API, например).

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
- [x] N1 Follow-up question buttons (Sprint 3).
- [x] N3 Human handover с context (Sprint 3).
- [x] N4 reply-threading (Sprint 3).
- [x] Eval pipeline + observability (response#1, observability#12).
- [x] Versioning metadata + section rerank (#3, #5).
- [ ] Retrieval polish: top-source соответствует домену вопроса (Sprint 4) — текущий MRR=0.28.
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
