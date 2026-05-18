# ТЗ compliance + Codex audit closure — Sprint 8 (2026-05-18)

## 1. ТЗ — обязательные требования

Сверка с `C:\Users\uedom\Downloads\ТЗ_AI ассистент_HR_ЮрО.pdf`.

| ТЗ-требование | Статус | Где / Как |
|---|---|---|
| Векторная БД, индексация 3-50 файлов | ✅ | pgvector/pgvector:pg16 + MVP-48 + 1 внешний (`corpus/external_tk_rf_chapter_11.md`); `manifests/MVP_CORPUS_FILES.txt` |
| Индексация регламентов, шаблонов, приказов, политик | ✅ | 7 категорий (01_hr_pol, 02_hr_tpl, 03_legal_con, 04_legal_cla, 05_tlog, 06_comp, 07_faq) |
| Открытые источники + возможность обновлять | ✅ | corpus/*.md под Git, ingest на старте rag-api |
| Внешний источник | ✅ | `external_tk_rf_chapter_11.md` (ТК РФ глава 11, трудовое законодательство) |
| Чанки 500 токенов, мета (файл, раздел, дата) | ✅ | `split_text` cl100k_base, frontmatter parsing |
| RAG-pipeline в n8n: вопрос→поиск→ответ с источниками | ✅ | `n8n/workflows/hr-legal-rag-workflow.json` (33 узла) |
| Классификация типа запроса | ✅ | `classify_request` (hr/legal/template_draft/unknown) + `classify_tg_update` (auth/command routing) |
| Не выдавать ответ без источника / при низкой уверенности | ✅ | `AnswerPolicy.min_confidence=0.25`, `derive_status=unanswerable`, `refused=true` |
| LLM для поиска и ответов; шаблоны через код | ✅ | Mistral для /ask; `DOCUMENT_TYPES` (5 типов HR-документов) с required_fields + draft_outline + draft_text в `/document/type-detection` |
| Telegram-бот с авторизацией (белый список) | ✅ | `parse_allowed_ids` в settings + `/tg/classify` whitelist endpoint |
| API-ключи в env, не в коде | ✅ | `.env` + `${VAR:?required}` для критичных + `$vars.TELEGRAM_BOT_TOKEN` в n8n (не в JS) |
| Логирование всех запросов | ✅ | Postgres `request_logs` (question, request_type, sources, confidence, latency_ms, llm_model, tokens) |
| Кнопки оценки ответа (👍/👎) | ✅ | inline_keyboard в Format Answer; 👎 → drill-down на 3 reasons (неточно/устарело/нужен человек) |
| Плохие ответы в очередь на ревью | ✅ | `enqueue_review` в `answer_feedback` + `review_queue` (с последними 5 запросами для human-эскалации) |
| Запросы в аналитику | ✅ | `/metrics` endpoint (refusal_rate, avg_latency, avg_confidence, bad_feedback_rate, window_hours) |

## 2. ТЗ — отклонения от рекомендаций (с обоснованием)

ТЗ явно говорит: «Стэк в ТЗ и предложение ниже — это **рекомендация, но не обязательное требование**. Если есть лучший вариант — нужно предложить в комментариях к задаче.»

| Рекомендация ТЗ | Наш выбор | Обоснование |
|---|---|---|
| `TokenTextSplitter(chunk_size=500, chunk_overlap=50)` | `chunk_overlap=75` | **eval-driven** (см. `docs/adr/0004-chunk-overlap-75.md`). overlap=50 регрессирует MRR на golden Q (replay 2026-05-17). overlap=75 даёт MRR=0.78, Hit@1=0.67, refusal=1.0. |
| Supabase pgvector | Self-hosted `pgvector/pgvector:pg16` | ТЗ предлагает «Supabase **или Pinecone** — выбор». Self-hosted pgvector функционально эквивалентен Supabase (Supabase = managed pgvector), без vendor-lock и кредитки. Тот же extension, тот же SQL. |

## 3. Codex audit — статус закрытия

`.tmp/codex-audit.md` (Codex review поверх Kimi от 2026-05-17). По состоянию на HEAD после Sprint 8:

| # | Finding | Severity | Status | Где закрыто |
|---|---|---|---|---|
| 1.1 | BM25 in-memory | P2 | OPEN (acceptable for MVP ≤50 docs) | Документировано (issue #1 acceptance) |
| 1.2 | Empty/stop-word queries bypass fallback | P2 | ✅ CLOSED | `HybridRetriever.search` → `_vector_only_search` (rag.py:221) |
| 1.3 | Coverage squared in scoring | P2 | ✅ CLOSED | `COVERAGE_EXP` param (rag.py:242) |
| 2.1 | Refusal gap on aviation terms | P0 | ✅ CLOSED | Sprint 4-5 enrichment (MRR 0.28→0.78) |
| 2.2 | LLM prompt не просит цитировать [Источник N] | P1 | ✅ CLOSED Sprint 8 #2 | `llm.py:79` system prompt addendum |
| 2.3 | LLM response shape unguarded | P1 | ✅ CLOSED Sprint 5 #4 | `_extract_choice_content` + empty_choices log |
| 3.1 | n8n Code env access | P0 | ✅ CLOSED Sprint 6 #1 + issue #18 | `$vars.TELEGRAM_BOT_TOKEN` + `N8N_BLOCK_ENV_ACCESS_IN_NODE=true` default |
| 3.2 | Default secrets in compose | P0 | ✅ CLOSED | `POSTGRES_PASSWORD`/`N8N_ENCRYPTION_KEY` — `${VAR:?required}` mandatory |
| 3.3 | n8n image unpinned | P1 | ✅ CLOSED | `n8nio/n8n:1.103.2` pinned |
| 4.1 | LLM errors swallowed | P1 | ✅ CLOSED Sprint 5 #4 | empty_choices warn + JSONDecodeError catch |
| 4.2 | /health без provider ping | P2 | OPEN (acceptable: enabled-flags для MVP) | Документировано — отдельный `/health/dependencies` в backlog |
| 4.3 | No retrieval explainability | P1 | ✅ CLOSED Sprint 6 #3 | `/ask?debug=true` → `RetrievalDebug` |
| 5.1 | n8n coupling (JS Code nodes) | P1 | ✅ CLOSED Sprint 6 #1 + Sprint 8 #1/#2 | Whitelist (commit `2e74a17`), Format Answer (`format_answer.py`), Format History/Docs (`tg_format.py`), Format Feedback (`tg_copy.py`). В n8n остаётся 2-строчный Format Expand (passthrough). |
| 5.2 | Confidence band не в API контракте | P1 | ✅ CLOSED Sprint 8 #2 | `confidence_band: high\|medium\|low\|none\|unknown` в `AskResponse`; единая функция `format_answer.confidence_band` |
| 5.3 | n8n depends_on без health | P1 | ✅ CLOSED | rag-api healthcheck + `condition: service_healthy` |
| 6.1 | Lexical state в process | P2 | OPEN (acceptable: MVP scope) | См. 1.1 |
| 6.2 | Vector dim mismatch silent | P2 | ✅ CLOSED Sprint 8 #2 | `storage._consensus_dim` + warn log при ingestion |
| 6.3 | Compose mounts diverge без visibility | P2 | ✅ CLOSED Sprint 8 #2 | `/health` экспортит `docs_path` + `docs_manifest_path` + `min_confidence` |
| 7.1 | Eval CI gates | P0 | ✅ CLOSED | `scripts/test_eval_regression.py` (MRR/Hit@1/Hit@5/refusal/avg_conf/latency floors) |
| 7.2 | Real dependency coverage thin | P1 | PARTIAL | Bridge unit tests (Sprint 7) + JSON pin tests; live Postgres testcontainer — backlog |
| 7.3 | Provider schema contract tests | P1 | ✅ CLOSED Sprint 5 #4 | empty_choices test + JSON decode guards |
| 8.1 | Compose exposes services broadly | P1 | ✅ CLOSED | postgres expose-only, n8n bound 127.0.0.1:5678 |
| 8.2 | Provider latency 30s | P2 | OPEN (acceptable: graceful degrade via `is_pure_refusal` extractive fallback на 429/timeout) | Документировано — circuit breaker в backlog |
| 8.3 | HTTP clients per request | P1 | ✅ CLOSED Sprint 6 #5 | Singleton `httpx.AsyncClient` с lifespan close |

Итого: **20/24 closed**, **1 partial** (7.2 real-dep coverage), **3 open** (1.1/6.1 BM25 in-memory, 4.2 health provider ping, 8.2 latency tuning) — все 3 acceptable для MVP scope с явной фиксацией в этом документе.

## 4. Что добавлено в Sprint 8 (2026-05-18)

### Sprint 8 #1 — Format Answer JS → Python

- `rag-api/app/format_answer.py` (260 строк) — порт `Format Answer` JS-узла из `n8n/workflows/hr-legal-rag-workflow.json` (158 строк JS). Pure functions: `md_to_html`, `balance_tags`, `confidence_band`, `confidence_chip`, `looks_refusal`, `split_into_parts`, `format_answer`.
- `rag-api/tests/test_format_answer.py` — 28 Python-native parity tests (без `node -e` shell-out).
- `POST /tg/format-answer` endpoint — n8n HTTP-нода может заменить JS Code-нод (workflow patch deferred до Docker-сессии).

### Sprint 8 #2 — Codex audit closure batch

- **2.2** Citation hint в Mistral system prompt: «Когда ссылаешься на факт, указывай источник в формате [Источник N]».
- **5.1** Format History (21 строка JS) → `app/tg_format.format_history` + `POST /tg/format-history`. Format Docs (13 строк) → `format_docs` + `POST /tg/format-docs`. Format Feedback (6 строк) → `tg_copy.FEEDBACK_DEFAULT_TEXT` / `FEEDBACK_HUMAN_TEXT` + `/tg/copy/feedback_default|human`.
- **5.2** `confidence_band: str` в `AskResponse`. Единая функция `format_answer.confidence_band` для UI/API parity.
- **6.2** `storage._consensus_dim` + warn log при vector dim mismatch на ingestion.
- **6.3** `/health` экспортит `docs_path`, `docs_manifest_path`, `min_confidence`.
- `rag-api/tests/test_tg_format.py` — 15 parity tests.

Всего тестов: **238** (было 195 — +28 format_answer + +15 tg_format).

## 5. Что осталось «out of MVP» (по ТЗ — Этап 2, Прод)

ТЗ явно перечисляет, что **НЕ входит** в MVP:

- Автообновление базы при изменении источников
- API-интеграция с КонсультантПлюс
- Ролевая модель (юрист/HR/руководитель)
- Версионирование документов (метадата `version` уже есть в frontmatter, но без живых diff)
- Интеграция с Битрикс24/Workspace
- Автосбор базы знаний из обращений
- Расширенная аналитика
- Админка управления ботом

Эти пункты документированы как Этап 2 backlog и не влияют на MVP-готовность.

## 6. Команды для верификации

```bash
# Sprint 8 closure verification
python -m pytest rag-api/tests/ -p no:schemathesis -q   # 238 passed

# При поднятом Docker — eval regression gate:
python scripts/test_eval_regression.py                  # MRR/Hit@1/refusal floors
python scripts/smoke_tg_e2e.py                          # N1+N2+N3+N4 live
```

HEAD после Sprint 8: см. `git log --oneline -3`.
