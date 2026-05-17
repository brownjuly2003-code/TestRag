# TestRag MVP Plan

## Goal

Собрать рабочий MVP HR/legal RAG-ассистента для авиагрузовой компании: Telegram-вопрос, n8n workflow, hybrid search по Postgres/pgvector + BM25, ответ через Mistral с источниками, логирование, оценка качества, drill-down feedback с категорией.

## Current Status

Updated: 2026-05-17 night (HEAD `74f45fd` — Sprint 5 closed).

- [x] Docker Compose поднят: `postgres` (expose-only, не публикуется), `rag-api` (с healthcheck), `n8n:1.103.2` (pinned), `cloudflared` (отдельный контейнер).
- [x] n8n workflow активирован, публичный webhook через cloudflare tunnel (trycloudflare).
- [x] Локальный Telegram whitelist для `432751211`.
- [x] RAG API: `chunk_count=189`, `documents=51` (MVP-47), postgres/mistral/embeddings enabled.
- [x] Postgres tables: documents (+version/effective_from/effective_to/status), document_chunks, request_logs (+latency_ms/llm_model/prompt_tokens/completion_tokens), answer_feedback (+category/free_text/chunk_ids), review_queue (+context jsonb).
- [x] **pytest 112/112** (`python -m pytest -p no:schemathesis`).
- [x] **Eval CI gate** активен: `pytest scripts/test_eval_regression.py` (floor MRR ≥0.60, Hit@1 ≥0.50, refusal ≥0.85).
- [x] Workflow 28 узлов активный (Sprint 3 N1 +4 ветки).
- [x] Aviation profile pass на 200 corpus-файлов; MVP-47 (+`07_faq_expedition/transport_road/claims_procedure`).
- [x] Sprint 4: aviation pollution revert в HR-шаблонах + не-safety политики (76 файлов).
- [x] Sprint 5 content enrichment: глоссарий controlled zone / AWB / MAWB / HAWB / ULD / GHA / cutoff / dangerous goods в `07_faq_expedition`, `05_tlog_regulation_waybill`, `01_hr_pol_safety`.
- [x] BCG demo polish: 🟢/🟡/🟠 confidence chip, refusal next-steps suffix, sources без bare score, /docs sample_files (2 doc-titles на категорию), README hero metrics.
- [x] LLM robustness guards: `_extract_choice_content`, JSONDecodeError catch, MistralEmbeddingClient._observed_dim warning при dim mismatch.
- [x] HybridRetriever weights env-параметризованы: HYBRID_{BM25,VECTOR,COVERAGE_EXP,SECTION_BOOST_*}.
- [x] Live TG E2E ✅ через `scripts/smoke_tg_e2e.py` (Telethon).

## Eval (10 golden Qs)

| Метрика | Pre-S4 | Post-S4 | **Post-S5** | Цель |
|---|---|---|---|---|
| Hit@1 | 0.22 | 0.44 | **0.67** | ≥0.60 ✓ |
| Hit@5 | 0.33 | 0.67 | **0.89** | ≥0.55 ✓ |
| MRR | 0.28 | 0.56 | **0.76** | ≥0.55 ✓✓ |
| Refusal accuracy | 0.70 | 0.70 | **1.00** | ≥0.90 ✓✓ |
| Avg confidence | 0.55 | 0.55 | **0.85** | — |
| p50 latency | 4.2 s | 4.2 s | 5.1 s | <8 s ✓ |

Baseline закоммичен — `eval/baseline.json` (НЕ `.tmp/`).

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

## Sprint 4 — retrieval polish ✅ DONE (2026-05-17, commit `9017878`)

Цель достигнута: MRR 0.28→0.56, Hit@5 0.33→0.67.

- [x] **Aviation pollution revert** (`docs/findings/2026-05-17-sprint4-retrieval-polish.md`): `git checkout 8aa97b9 --` для 76 файлов (01_hr/02_hr_tmp/07_faq кроме aviation-FAQ; 01_hr_pol_safety оставлен).
- [x] Удалён `test_aviation_profile_in_hr_probation` (кодифицировал bug-as-feature).
- [x] Eval expected_file Q5: `01_hr_pol` → `01_hr_probation`.

## BCG demo polish ✅ DONE (2026-05-17, commit `fe22106`)

- [x] Format Answer: 🟢/🟡/🟠 confidence chip перед ответом (≥0.7/0.4/0); refusal-aware «Что делать дальше» suffix.
- [x] Sources без bare score; «Источники:» / «Ближайшие документы (вне ответа):» для refusal.
- [x] Whitelist /start: hero + value-prop + 3 example questions.
- [x] Whitelist /help: «Что я умею» / «Примеры» / «Команды».
- [x] /docs/summary +sample_files (по 2 на категорию через DISTINCT+ROW_NUMBER).
- [x] README hero block с retrieval-метриками pre/post.
- [x] +6 pin тестов (confidence chip, refusal detection, no-score, /docs samples).

## Sprint 5 — content enrichment + audit hardening ✅ DONE (2026-05-17 night, commit `74f45fd`)

Цель: закрыть P0/P1 из Kimi + Codex cross-audit (`.tmp/{kimi,codex}-audit.md`). MRR 0.56→0.76, refusal 0.70→1.00.

- [x] **#1 Content enrichment** (P0): глоссарий controlled zone / AWB / MAWB / HAWB / ULD / GHA / cutoff / dangerous goods в `07_faq_expedition` + `05_tlog_regulation_waybill` + `01_hr_pol_safety`. MVP-44 → MVP-47.
- [x] **#2 Eval CI regression gate** (P0): `scripts/test_eval_regression.py` (7 pytest gate'ов с floor'ами); `eval/baseline.json` (НЕ .tmp/) закоммичен; eval_retrieval.py `expected_files` (список).
- [x] **#3 Compose hardening** (P1): n8n:1.103.2 (pin), `${POSTGRES_PASSWORD:?required}` / `${N8N_ENCRYPTION_KEY:?required}` fail-fast, rag-api healthcheck, n8n `depends_on rag-api: service_healthy`, postgres expose-only (без publish).
- [x] **#4 LLM robustness** (P1, codex-audit#2.3/7.3/6.2): `_extract_choice_content` guard, JSONDecodeError catch в `_loads_json_object`, `MistralEmbeddingClient._observed_dim` pin + warning при mismatch, ValueError catch на response.json(), structured logger.warning.
- [x] **#5 Hybrid weights env-параметризация** (P1): `HYBRID_BM25_WEIGHT/VECTOR_WEIGHT/COVERAGE_EXP/SECTION_BOOST_PER_TERM/SECTION_BOOST_MAX` через env (defaults = Sprint 5 baseline).

## Sprint 6 — extract + observability (NEXT, не делаю в этой сессии)

Backlog из Kimi+Codex consensus, требует архитектурного шага.

- [ ] **Extract business logic из n8n в rag-api**: whitelist check, command routing, /help/start/clear copy → FastAPI endpoints `/auth/check`, `/commands`. После — `N8N_BLOCK_ENV_ACCESS_IN_NODE=true`. ~1 день.
- [ ] **OpenAPI export**: `/openapi.json` → `docs/openapi.yaml` в repo + ADR (n8n choice, BM25 in-memory, Mistral). ~4 часа.
- [x] **Retrieval explainability** (codex-audit#6.3): `AskRequest.debug=true` → `AskResponse.debug` с `query_tokens`, `weights` (BM25/Vector/coverage_exp/section_boost), `has_vector`, per-result rows (`bm25_score`/`normalized_bm25`/`vector_score`/`coverage`/`section_boost`/`final_score`). `SearchResult` расширен полями `coverage`/`section_boost`/`normalized_bm25` (defaults сохраняют backwards-compat). 2 unit-теста (default null + breakdown shape). pytest 117/117, eval gate 7/7.
- [x] **Empty/stop-word query fallback** (codex-audit MISSED 1.2): `HybridRetriever._vector_only_search` — на `query_tokens=[]` отдаём top-K по cosine, иначе `[]` (нет embedding/нет chunk-embeddings). 3 unit-теста. Live: stop-word query «а или и» → 3 sources score≈0.87, LLM сам отвергает через `is_pure_refusal` гард.
- [x] **HTTP client pooling** (codex-audit MISSED 8.3): `MistralChatClient._async_client`/`MistralEmbeddingClient._async_client` singleton lazy-init (`_get_async_client`), backed by `aclose()` cleanup из FastAPI `lifespan`. Per-call `async with httpx.AsyncClient(...)` заменён на shared instance в trёх async hot-paths (chat.answer, chat.document_plan, embed_query). Eval CI gate 71s → **29s (-60%)** на 10 golden Qs.
- [ ] **N2 Quick-actions**: «Уточнить» (top_k=10 rerun), «Развернуть» (full chunk content). ~3 часа.
- [ ] **Prev-N-QA в retrieval**: ablation A/B на golden Q. ~3 часа.

## Sprint 7+ — production hardening (если потребуется)

- [ ] **Structure-aware chunking**: split по markdown `##`/`###` headers вместо фиксированных 500 токенов.
- [ ] **Cross-encoder reranker** (BGE-Reranker-v2-m3) на top-20 → top-5.
- [ ] **SSO + RLS**: per-user role + Postgres RLS на document_chunks.
- [ ] **External normative ingestion**: один lawsource live-обновляемый (КонсультантПлюс API).
- [ ] **Langfuse** observability: трассировка LLM-вызовов, стоимость, drift detection.
- [ ] **RAGAS** auto-eval: faithfulness, answer_relevancy, context_precision на golden set.

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
- [x] Retrieval polish: MRR=0.76, Hit@1=0.67, refusal_accuracy=1.00 на golden set (Sprint 4+5).
- [x] Eval CI regression gate (`pytest scripts/test_eval_regression.py`) предотвращает регрессию retrieval.
- [ ] MVP можно показать без покупки n8n Cloud по `docs/demo-runbook.md` (зависит от cloudflare named tunnel или paid n8n).

## Known Issues

Полный список в `docs/known-issues.md`. Главные:

| # | issue | severity | fix |
|---|---|---|---|
| 1 | ~~Retrieval polluted после aviation pass~~ | RESOLVED Sprint 4 | commit `9017878` |
| 2 | TG webhook secret in-memory | low (только тестирование) | n/a (n8n upstream) |
| 7 | Mistral free tier 429 | medium (prod) | paid tier для prod |
| 10 | Cloudflare tunnel эфемерные URLs | medium (demo) | named tunnel или real domain |
| 14 | n8n coupling (whitelist/copy в JS nodes) | medium (Kimi+Codex audit) | Sprint 6 extract |
| 15 | Postgres 127.0.0.1 binding blocked on Windows Docker | low (Hyper-V dynamic port reservation) | expose-only, firewall в prod |

## Notes

- n8n используется как оркестратор, RAG-логика остается в коде (rag-api/app).
- Retrieval гибридный: pgvector + BM25, оба BM25 и vector scores combined с весами в HybridRetriever.
- LLM и embeddings: Mistral. Free tier хватает для demo, для prod нужен paid tier (issue 7).
- Workflow 24 узла, активно `executionOrder=v1`.
- TG callback_data 64-byte лимит влияет на N1 design (см. Sprint 3).
- После любого изменения rag-api Python: `docker compose build rag-api && docker compose up -d --force-recreate rag-api` (см. issue 9).
- После изменения workflow JSON: re-import через CLI с `MSYS_NO_PATHCONV=1` (issue 8).
