# TestRag MVP Plan

## Goal

Собрать рабочий MVP HR/legal RAG-ассистента для авиагрузовой компании: Telegram-вопрос, n8n workflow, hybrid search по Postgres/pgvector + BM25, ответ через Mistral с источниками, логирование, оценка качества, drill-down feedback с категорией.

## Current Status

Updated: 2026-05-17 night (HEAD `8d7adf2` — Sprint 6 #1 closure через $vars + 📖 expand fix + /expand HTML escape + n8n upgrade deferred).

- [x] Docker Compose поднят: `postgres` (expose-only, не публикуется), `rag-api` (с healthcheck), `n8n:1.103.2` (pinned), `cloudflared` (отдельный контейнер).
- [x] n8n workflow активирован (**33 узла**, +Format Expand night-fix), публичный webhook через cloudflare tunnel (trycloudflare).
- [x] Локальный Telegram whitelist для `432751211`.
- [x] RAG API: `chunk_count=583`, `documents=52` (MVP-48 включая `external_tk_rf_chapter_11.md`), postgres/mistral/embeddings enabled, **token-based splitter cl100k_base 500/75, min_conf=0.25**.
- [x] Postgres tables: documents (+version/effective_from/effective_to/status), document_chunks, request_logs (+latency_ms/llm_model/prompt_tokens/completion_tokens), answer_feedback (+category/free_text/chunk_ids), review_queue (+context jsonb).
- [x] `n8n.variables.TELEGRAM_BOT_TOKEN` инсертится через `scripts/seed_n8n_vars.py` (issue #18 fix: `$vars` вместо `$env`, `N8N_BLOCK_ENV_ACCESS_IN_NODE=true` default).
- [x] **pytest 193/193** (+1 night HTML escape lock-in).
- [x] **Eval CI gate** активен: `pytest scripts/test_eval_regression.py` (floor MRR ≥0.60, Hit@1 ≥0.50, refusal ≥0.85).
- [x] Aviation profile pass на 200 corpus-файлов; MVP-48 (+external_tk_rf_chapter_11.md).
- [x] Sprint 4: aviation pollution revert в HR-шаблонах + не-safety политики (76 файлов).
- [x] Sprint 5 content enrichment: глоссарий controlled zone / AWB / MAWB / HAWB / ULD / GHA / cutoff / dangerous goods в `07_faq_expedition`, `05_tlog_regulation_waybill`, `01_hr_pol_safety`.
- [x] BCG demo polish: 🟢/🟡/🟠 confidence chip, refusal next-steps suffix, sources без bare score, /docs sample_files (2 doc-titles на категорию), README hero metrics.
- [x] LLM robustness guards: `_extract_choice_content`, JSONDecodeError catch, MistralEmbeddingClient._observed_dim warning при dim mismatch.
- [x] HybridRetriever weights env-параметризованы: HYBRID_{BM25,VECTOR,COVERAGE_EXP,SECTION_BOOST_*}.
- [x] **Live TG E2E 6/6 ✅** через `scripts/smoke_tg_e2e.py` (Telethon): N1 followup, N2 🔁 clarify + 📖 expand, N3 human handover, N4 reply threading.

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

## Sprint 6 — extract + observability ✅ DONE (2026-05-17)

Backlog из Kimi+Codex consensus + Kimi audit (`kimi_audit_17_05_26.md`).

- [x] **#1 Extract business logic из n8n в rag-api** (commit `2e74a17`): `tg_classifier.py` + `tg_copy.py` (118 строк JS → Python с parity-тестами); `POST /tg/classify` (whitelist+routing+copy), `GET /tg/copy/{key}` (single point of edit). Whitelist Code node — тонкий HttpRequest proxy на `http://rag-api:8000/tg/classify`. `N8N_BLOCK_ENV_ACCESS_IN_NODE=true` в docker-compose. ALLOWED_TELEGRAM_USER_IDS теперь в rag-api env. Closes Issue #14 codex-audit#3. +32 unit-теста.
- [x] **#2 OpenAPI export**: `scripts/export_openapi.py` → `docs/openapi.yaml` + `docs/openapi.json` (12 paths, 23 schemas после Sprint 6 #1+#6). Pytest gate `test_openapi_contract.py` (4 теста: schema-drift, required paths, debug field в request/response). ADR'ы в `docs/adr/`: 0001 (n8n choice), 0002 (in-memory BM25 + pgvector), 0003 (Mistral).
- [x] **#3 Retrieval explainability** (codex-audit#6.3): `AskRequest.debug=true` → `AskResponse.debug` с `query_tokens`, `weights`, `has_vector`, per-result breakdown. `SearchResult` расширен `coverage`/`section_boost`/`normalized_bm25`.
- [x] **#4 Empty/stop-word query fallback** (codex-audit MISSED 1.2): `HybridRetriever._vector_only_search` — на `query_tokens=[]` отдаём top-K по cosine.
- [x] **#5 HTTP client pooling** (codex-audit MISSED 8.3): singleton httpx.AsyncClient + `aclose()` в FastAPI lifespan. Eval CI gate 71s → **29s (-60%)**.
- [x] **#6 N2 Quick-actions** (commit `217b84f`): `POST /clarify` (rerun original Q с top_k=10), `GET /expand` (full chunk content). Format Answer +row 3 (🔁 Уточнить + 📖 Развернуть). n8n workflow +Clarify?/Expand? IF branches +Resolve Clarify/Expand HTTP nodes (28→32 узла). +14 unit-тестов.
- [x] **#7 Prev-N-QA infrastructure** (commit `50699fe`): `multiturn.py` (`augment_retrieval_query` + `filter_relevant_prev_qas` skip refusal/low-conf), `AskRequest.prev_qa_count: int = 0` opt-in (0..5), augmentation идёт ТОЛЬКО в retrieval (embedding + BM25), не в LLM prompt (защита от дрейфа). `scripts/eval_multiturn.py` — 5 multi-turn cases A/B harness. +15 unit-тестов. **Live A/B отложен** (Docker cold start, см. docs/known-issues.md #16).

## Sprint 6 EOS+Night closures (2026-05-17 follow-up sessions)

- [x] **Eval replay overlap=50 → rollback к 75** (commit `52ed0a5`, ADR-0004): floor-violation подтверждена (MRR 0.78→0.56, refusal 1.00→0.70). MIN_CONFIDENCE drift 0.35→0.25 (issue #19). Final baseline: MRR 0.78, Hit@1 0.67, Hit@5 1.00, refusal_acc 1.00, avg_conf 0.80.
- [x] **Prev-N-QA live A/B** (commit `52ed0a5`): ΔHit@1=0, ΔHit@5=+0.20, ΔMRR=+0.05. Решение — opt-in default=0.
- [x] **TG E2E smoke с 🔁/📖**: `scripts/smoke_tg_e2e.py` расширен N2 buttons. **6/6 ✓** на HEAD `254d670` после Format Expand fix.
- [x] **n8n workflow import после Sprint 6 правок**: SQL UPDATE workaround (issue #17, `.tmp/update_workflow.sql` + docker cp + psql + restart). CLI broken на 1.103.2 (column `User.role does not exist` → ALTER TABLE alias-колонка).
- [x] **Sprint 6 #1 finish** (commit `a54752a`, closes issue #18): 4 TG HTTP-ноды (Send Typing / Typing FU / Edit Reply Markup / Send Answer) → `$vars.TELEGRAM_BOT_TOKEN` вместо `$env`. `N8N_BLOCK_ENV_ACCESS_IN_NODE=true` default восстановлен. `scripts/seed_n8n_vars.py` для clean-DB onboarding.
- [x] **📖 expand workflow bug** (commit `254d670`): Resolve Expand отдавал ExpandResponse без chat_id → Send Direct Reply падал TG 400. Insert Format Expand Code-узла (33 узла, было 32). Smoke 6/6.
- [x] **`/expand` HTML escape** (commit `8d7adf2`): chunk.content шёл в f-string без `html.escape` → TG 400 "can't parse entities" на chunks с `<https://...>`/`M&A`/`P&L`. Latent bug (smoke случайно ловил безопасный chunk).
- [x] **n8n upgrade research → deferred** (issue #17 resolution в `docs/known-issues.md`): ALTER alias-колонка решила User.role error для runtime+CLI. CLI import всё ещё требует канонической JSON-формы (versionId/createdAt/...) → git noise. SQL UPDATE сохраняет webhook secret. Upgrade пересматривать when scaling/feature/CVE.

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
| 14 | ~~n8n coupling (whitelist/copy в JS nodes)~~ | ✅ RESOLVED Sprint 6 #1 (`2e74a17`) | — |
| 15 | Postgres 127.0.0.1 binding blocked on Windows Docker | low (Hyper-V dynamic port reservation) | expose-only, firewall в prod |
| 16 | Docker Desktop cold start ≥10мин на Win11+WSL2 | medium (блокирует live eval/smoke) | pre-warm Docker UI заранее, defer eval-replay |
| 17 | n8n 1.103.2 CLI/schema mismatch (`User.role`) | low (ALTER alias-колонка покрыла) | SQL UPDATE workaround. Upgrade deferred (см. known-issues.md) |
| 18 | ~~Sprint 6 #1 partial: HTTP-ноды на `$env`~~ | ✅ RESOLVED 2026-05-17 night (`a54752a`) | `$vars.TELEGRAM_BOT_TOKEN` через `scripts/seed_n8n_vars.py` |
| 19 | MIN_CONFIDENCE drift в `.env` (0.35 vs 0.25) | low (resolved в 2026-05-17 EOS) | дефолт 0.25 в docker-compose.yml фиксирует |

## Notes

- n8n используется как оркестратор, RAG-логика остается в коде (rag-api/app).
- Retrieval гибридный: pgvector + BM25, оба BM25 и vector scores combined с весами в HybridRetriever.
- LLM и embeddings: Mistral. Free tier хватает для demo, для prod нужен paid tier (issue 7).
- Workflow 24 узла, активно `executionOrder=v1`.
- TG callback_data 64-byte лимит влияет на N1 design (см. Sprint 3).
- После любого изменения rag-api Python: `docker compose build rag-api && docker compose up -d --force-recreate rag-api` (см. issue 9).
- После изменения workflow JSON: re-import через CLI с `MSYS_NO_PATHCONV=1` (issue 8).
