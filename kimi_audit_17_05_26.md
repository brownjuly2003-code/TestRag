# Полный аудит проекта TestRag

**Дата аудита:** 2026-05-17  
**Версия кода:** HEAD `116b67f` (post-Fix#1/#2, Sprint 5 closed, Sprint 6 partial)  
**Аудитор:** Kimi Code CLI  
**Проект:** RAG-ассистент для HR и Legal (авиагрузовая вертикаль) — Telegram-бот, hybrid retrieval, генерация ответов с источниками.  

---

## 1. Executive Summary

TestRag — это зрелый MVP RAG-системы для HR/legal домена, перепрофилированный под авиагрузовую компанию. Кодовая база демонстрирует высокую культуру разработки: 131 юнит-тестов (100% pass), закоммиченный eval baseline, регрессионные гейты, структурированная документация (ADR, runbook, findings) и систематический подход к исправлению проблем (Sprint 1–5).

**Ключевые метрики качества (10 golden questions):**
- Hit@1: **0.67** (цель ≥0.60 ✓)
- Hit@5: **1.00** (цель ≥0.55 ✓)
- MRR: **0.78** (цель ≥0.55 ✓)
- Refusal accuracy: **1.00** (цель ≥0.90 ✓)
- Средняя latency: **6.1 с** (цель <8 с ✓)

**Общая оценка:** 🟢 **Демо-готов.** Для production требуется Sprint 6 (extract business logic из n8n) и переход на paid-tier LLM.

---

## 2. Архитектура и стек технологий

```
Пользователь (Telegram) → n8n (оркестратор) → RAG API (FastAPI) → Postgres/pgvector
                                    ↓
                              Mistral LLM + Embeddings
```

| Компонент | Технология | Роль |
|---|---|---|
| **Bot UI** | Telegram (webhook) | Пользовательский интерфейс |
| **Orchestrator** | n8n 1.103.2 (self-hosted) | Маршрутизация, whitelist, логирование, кнопки оценки |
| **RAG API** | FastAPI 0.115.6 (Python 3.13) | Классификация, hybrid retrieval, генерация ответа |
| **Vector Store** | Postgres 16 + pgvector | Хранение чанков, embeddings, логов, feedback, review queue |
| **LLM** | Mistral (mistral-small-latest) | Chat + embeddings (mistral-embed) |
| **Chunking** | tiktoken cl100k_base | Token-based splitter (500 токенов, overlap 75) |
| **Retrieval** | In-memory BM25 + pgvector cosine | Hybrid scoring с section-keyword rerank |
| **Infra** | Docker Compose | 3 сервиса + cloudflared (tunnel) |

### Архитектурные решения (ADR)
- **ADR-0001:** n8n как orchestrator (Accepted, планируется re-evaluate в Sprint 6+)
- **ADR-0002:** In-memory BM25 + pgvector hybrid (Accepted, threshold ~5000 чанков)
- **ADR-0003:** Mistral для chat + embeddings (Accepted, re-evaluate при rate-limit на проде)

### Разделение ответственности
Ответственность чётко разделена между компонентами. n8n отвечает за транспорт и UI-логику, RAG API — за доменную логику поиска и генерации, Postgres — за персистентность. Это соответствует принципу единственной ответственности.

---

## 3. Структура проекта

```
TestRag/
├── corpus/                    # 200 документов (.md), 7 категорий
├── manifests/
│   ├── MVP_CORPUS_FILES.txt   # 47 файлов для MVP-индексации
│   └── NORMATIVE_SOURCE_MANIFEST.md  # Каталог внешних источников
├── rag-api/
│   ├── app/
│   │   ├── main.py            # FastAPI endpoints (905 строк)
│   │   ├── rag.py             # HybridRetriever, chunking, scoring (339 строк)
│   │   ├── llm.py             # Mistral chat + embedding clients (269 строк)
│   │   ├── storage.py         # PostgresStore, frontmatter parsing (532 строк)
│   │   └── settings.py        # Pydantic-like Settings dataclass (33 строки)
│   ├── tests/
│   │   ├── test_api.py        # 28 тестов (API contract, feedback, history)
│   │   ├── test_rag.py        # 18 тестов (retrieval, chunking, BM25)
│   │   ├── test_llm.py        # 9 тестов (Mistral guards, JSON parsing)
│   │   ├── test_n8n_workflow.py  # 62 теста (workflow JS nodes, routing)
│   │   ├── test_openapi_contract.py  # 4 теста (schema drift)
│   │   └── test_ingestion.py  # 10 тестов (ingest, frontmatter, backfill)
│   ├── requirements.txt       # 7 зависимостей (минимальный набор)
│   └── Dockerfile             # Лёгкий образ
├── n8n/workflows/
│   └── hr-legal-rag-workflow.json  # 28 узлов
├── sql/init.sql               # Схема БД + миграции ALTER TABLE
├── scripts/
│   ├── eval_retrieval.py      # 10 golden questions eval
│   ├── test_eval_regression.py    # Pytest regression gate (7 тестов)
│   ├── export_openapi.py      # Генерация docs/openapi.{yaml,json}
│   └── smoke_tg_e2e.py        # Telethon E2E smoke
├── docs/
│   ├── adr/                   # 3 ADR
│   ├── findings/              # Deep-dive аналитика
│   ├── research/              # UX-исследования, synthesis
│   ├── demo-runbook.md        # Пошаговая инструкция для демо
│   ├── known-issues.md        # 15 issues с workaround/fix status
│   ├── next-session.md        # Handoff для следующей сессии
│   └── openapi.{yaml,json}    # OpenAPI spec (8 paths, 19 schemas)
├── eval/baseline.json         # Закоммиченный baseline (10 Qs)
├── docker-compose.yml         # 3 сервиса + volumes
├── pytest.ini                # Конфигурация pytest
└── README.md                 # 371 строка: value-prop, метрики, quickstart
```

---

## 4. Качество кода

### 4.1. Читаемость и структура
- **FastAPI endpoints** чётко структурированы: `AskRequest`/`AskResponse`, `FeedbackRequest`, `HistoryResponse`, `MetricsResponse`, `DocumentTypeRequest/Response`.
- **Pydantic модели** используются для валидации входных/выходных данных.
- **Dataclass `Runtime`** инкапсулирует зависимости (chunks, retriever, policy, llm, embeddings, store).
- **@lru_cache на `get_runtime()` и `get_settings()`** — корректное singleton-поведение.
- **Lifespan cleanup** (`@asynccontextmanager`) — graceful shutdown singleton httpx клиентов.

### 4.2. Обработка ошибок
- **LLM guards:** `_extract_choice_content` защищает от `KeyError`/`IndexError` при пустом `choices`. JSONDecodeError ловится в `_loads_json_object`.
- **Embedding dim pin:** `MistralEmbeddingClient._observed_dim` логирует warning при несовпадении размерности векторов.
- **Graceful degrade:** если Mistral API недоступен (429, timeout), система возвращает extractive answer из найденных чанков без падения.
- **Pure refusal detection:** `is_pure_refusal()` отличает осторожный lead-in («Данных недостаточно...») от полного отказа, предотвращая ложные refusal'ы.

### 4.3. Конфигурируемость
- **HybridRetriever weights** параметризуются через env: `HYBRID_BM25_WEIGHT`, `HYBRID_VECTOR_WEIGHT`, `HYBRID_COVERAGE_EXP`, `HYBRID_SECTION_BOOST_PER_TERM`, `HYBRID_SECTION_BOOST_MAX`.
- **MIN_CONFIDENCE** перекалибруется через env (default 0.25 после перехода на token-splitter).
- **Manifest mode:** `DOCS_MANIFEST_PATH` ограничивает индексацию выбранными файлами.

### 4.4. Дублирование кода
- **Acceptable:** `_iter_document_files` продублирован в `main.py` и `storage.py`. Небольшая цена за отсутствие циклических импортов.
- **Resolved:** `split_text` единый в `rag.py`, `storage.py` импортирует его оттуда (Fix #2).

### 4.5. Типизация
- Используется `from __future__ import annotations` во всех модулях.
- Типы покрывают публичные интерфейсы и внутренние функции. Есть небольшие пробелы в `storage.py` (cursor как `Any`), но они оправданы psycopg API.

---

## 5. Тестирование

### 5.1. Покрытие и результаты
```
131 passed in 4.10s (Windows, Python 3.13.7, pytest-8.4.2)
```

| Модуль | Тесты | Что покрывают |
|---|---|---|
| `test_api.py` | 28 | API endpoints, feedback, history, metrics, followup, document type detection, refusal logic |
| `test_rag.py` | 18 | BM25 scoring, section boost, confidence, token splitter, vector fallback, aviation queries |
| `test_llm.py` | 9 | Choice extraction guards, JSON parsing, dim mismatch warning |
| `test_n8n_workflow.py` | 62 | JS Code nodes (Format Answer, Whitelist, routing), HTML escape, split logic, balanceTags |
| `test_openapi_contract.py` | 4 | Schema drift между кодом и docs/openapi.yaml |
| `test_ingestion.py` | 10 | Frontmatter parsing, chunk diff detection, embedding backfill, manifest filtering |

### 5.2. Регрессионные гейты
- **Eval CI gate:** `pytest scripts/test_eval_regression.py` — 7 тестов с floor'ами (MRR ≥0.60, Hit@1 ≥0.50, refusal ≥0.85).
- **OpenAPI contract gate:** ловит drift между FastAPI моделями и документированной схемой.

### 5.3. E2E тестирование
- `scripts/smoke_tg_e2e.py` — Telethon-based E2E через реальный Telegram-бот (@AIagentJu_bot).
- Покрывает: отправку вопроса, reply threading, follow-up кнопки, 👎/🧑‍💼 feedback, human handover ACK.

### 5.4. Качество тестов
- Тесты используют `monkeypatch` + `FakeStore`/`FakeDocumentPlanner` — быстрые, не требуют живой БД.
- Есть корпус-тесты (`test_probation_corpus_says_extension_is_not_allowed`, `test_aviation_profile_in_dangerous_goods_regulation`) — проверяют содержимое markdown-файлов.

---

## 6. Метрики Retrieval (RAG качество)

### 6.1. Текущий baseline (eval/baseline.json)

| Метрика | Значение | Цель | Статус |
|---|---|---|---|
| Hit@1 | 0.667 | ≥0.60 | ✅ |
| Hit@5 | 1.000 | ≥0.55 | ✅ |
| MRR | 0.782 | ≥0.55 | ✅ |
| Refusal accuracy | 1.000 | ≥0.90 | ✅ |
| Avg confidence | 0.798 | — | — |
| Avg latency | 6.1 с | <8 с | ✅ |

### 6.2. Эволюция метрик

| Этап | Hit@1 | Hit@5 | MRR | Refusal |
|---|---|---|---|---|
| Pre-Sprint 4 | 0.22 | 0.33 | 0.28 | 0.70 |
| Post-Sprint 4 | 0.44 | 0.67 | 0.56 | 0.70 |
| Post-Sprint 5 | 0.67 | 0.89 | 0.76 | 1.00 |
| Post-Fix#1/#2 | **0.67** | **1.00** | **0.78** | **1.00** |

### 6.3. Retrieval алгоритм
**HybridRetriever** комбинирует:
1. **BM25** (вес по умолчанию 0.65) — in-memory, русская стеммизация (suffix stripping), стоп-слова.
2. **Vector cosine** (вес 0.35) — pgvector embeddings, normalized to [0,1].
3. **Coverage exponent** (2.0) — штрафует чанки, покрывающие мало query-термов.
4. **Section boost** (+10% per term, cap +30%) — повышает чанки, у которых section совпадает с query.

**Плюсы:**
- Алгоритм интерпретируемый (debug breakdown в `/ask?debug=true`).
- Веса параметризуются через env без пересборки.

**Минусы:**
- BM25 in-memory ограничен ~5000 чанками (ADR-0002). При масштабировании — переход на pg_trgm или внешний Elasticsearch.
- Нет cross-encoder reranker (BGE-Reranker) — потенциал для улучшения top-K precision.

---

## 7. Безопасность

### 7.1. Сделано хорошо ✅
- **Secrets в env:** `TELEGRAM_BOT_TOKEN`, `MISTRAL_API_KEY`, `POSTGRES_PASSWORD`, `N8N_ENCRYPTION_KEY` — не хранятся в коде.
- **Postgres expose-only:** порт 5432 не публикуется наружу (Sprint 5 hardening). Доступ только через docker-network.
- **Whitelist авторизация:** Telegram-бот отвечает только пользователям из `ALLOWED_TELEGRAM_USER_IDS`.
- **Path traversal защита:** `_iter_document_files` проверяет `is_relative_to(root_path)`.
- **SQL-инъекции:** Используется psycopg с параметризованными запросами (`%s` placeholders).
- **Input validation:** Pydantic модели с `Field(min_length=1)`, clamping (`limit = max(1, min(limit, 20))`).

### 7.2. Зоны риска ⚠️
- **N8N_BLOCK_ENV_ACCESS_IN_NODE=false** (Issue #14): n8n workflow читает env напрямую в JS Code nodes. Это требуется для whitelist-логики, но ослабляет изоляцию.
  - *Mitigation:* Sprint 6 backlog — вынести whitelist в FastAPI endpoint `/auth/check`, после чего установить `N8N_BLOCK_ENV_ACCESS_IN_NODE=true`.
- **n8n business logic coupling:** Whitelist check, command routing, Format Answer (MD→HTML, split, balanceTags) — всё в JS Code nodes внутри workflow JSON. Изменение = re-import + restart.
  - *Mitigation:* Sprint 6 — extract в FastAPI endpoints.
- **Cloudflare ephemeral tunnel:** trycloudflare URLs меняются при пересоздании контейнера. TG webhook указывает на dead URL → бот молчит.
  - *Mitigation:* named tunnel ($0 для personal use, требует домена) или собственный VPS.
- **Отсутствие HTTPS/TLS termination:** RAG API и n8n работают по HTTP внутри docker network. Для production — нужен reverse proxy с TLS.
- **Нет rate limiting на /ask:** Быстрая последовательность запросов может триггерить Mistral 429. Graceful degrade есть, но throttle на уровне API отсутствует.

---

## 8. Инфраструктура и DevOps

### 8.1. Docker Compose
```yaml
services:
  postgres:   pgvector/pgvector:pg16  (expose-only, healthcheck)
  rag-api:    local build              (port 8000, depends_on postgres healthy)
  n8n:        n8nio/n8n:1.103.2        (port 5678, pinned version)
```

**Hardening (Sprint 5):**
- `${POSTGRES_PASSWORD:?required}` / `${N8N_ENCRYPTION_KEY:?required}` — fail-fast при отсутствии.
- `restart: unless-stopped` на всех сервисах.
- rag-api healthcheck через urllib (timeout=3).
- n8n `depends_on rag-api: condition: service_healthy`.

### 8.2. Базы данных
- **pgvector** для embeddings (ivfflat index, 1024 dim, 100 lists).
- **tsvector** (GIN index) для PostgreSQL full-text fallback.
- **Схема:** 5 таблиц + ALTER TABLE миграции (versioning, observability columns).

### 8.3. CI/CD и автоматизация
- Нет полноценного CI pipeline, но есть **локальные гейты:**
  - `pytest -p no:schemathesis` (131 тестов)
  - `pytest scripts/test_eval_regression.py` (7 eval regression тестов)
  - `pytest rag-api/tests/test_openapi_contract.py` (schema drift)
- **OpenAPI export:** `python scripts/export_openapi.py` → `docs/openapi.{yaml,json}`.

### 8.4. Known Infrastructure Issues
- **Issue #9:** rag-api требует `docker compose build` после изменения `.py` (нет volume mount source). Trade-off: snapshot-based деплой vs hot-reload.
- **Issue #8:** n8n CLI path mangling на Windows + Git Bash. Workaround: `MSYS_NO_PATHCONV=1`.
- **Issue #15:** Hyper-V dynamic port reservation на Windows. Workaround: postgres expose-only.

---

## 9. Документация

### 9.1. Оценка: Отлично ⭐
Проект имеет одну из самых полных документаций среди MVP:

| Документ | Назначение | Качество |
|---|---|---|
| `README.md` (371 строка) | Value-prop, метрики, quickstart, архитектура, риски | ⭐⭐⭐⭐⭐ |
| `docs/demo-runbook.md` | Пошаговое демо с командами, webhook, tunnel | ⭐⭐⭐⭐⭐ |
| `docs/known-issues.md` | 15 issues: симптом → root cause → status → workaround | ⭐⭐⭐⭐⭐ |
| `docs/next-session.md` | Handoff для следующей сессии с контекстом | ⭐⭐⭐⭐⭐ |
| `docs/adr/` | 3 ADR с rationale и trade-offs | ⭐⭐⭐⭐⭐ |
| `docs/findings/` | Deep-dive аналитика (retrieval polish) | ⭐⭐⭐⭐⭐ |
| `docs/research/` | UX-исследования, synthesis | ⭐⭐⭐⭐ |
| `mvp-plan.md` | Sprint roadmap, done-when criteria | ⭐⭐⭐⭐⭐ |
| `to_fix.md` | ТЗ-фиксы с оценкой effort и порядком выполнения | ⭐⭐⭐⭐⭐ |
| `eval/baseline.json` | Закоммиченный baseline с per-question breakdown | ⭐⭐⭐⭐⭐ |
| `docs/openapi.{yaml,json}` | API contract, 8 paths, 19 schemas | ⭐⭐⭐⭐⭐ |

### 9.2. Комментарии в коде
- Комментарии структурированы и содержат context: «Fix #2», «Sprint 6 #3», «codex-audit#6.3».
- История изменений прослеживается по git blame + комментариям.

---

## 10. Корпус данных

### 10.1. Состав
- **200 файлов** в `corpus/`, 7 категорий:
  - `01_hr_pol_*` — HR политики (43 файла)
  - `02_hr_tmp_*` — HR шаблоны (25 файлов)
  - `03_legal_contract_*` — Legal договоры (38 файлов)
  - `04_legal_claim_*` — Legal претензии (19 файлов)
  - `05_tlog_*` — Транспорт и логистика (31 файл)
  - `06_comp_*` — Комплаенс (17 файлов)
  - `07_faq_*` — FAQ (10 файлов)
  - `external_tk_rf_chapter_11.md` — Внешний нормативный источник (ТК РФ, гл. 11)

### 10.2. Качество контента
- **Sprint 4:** Исправлен aviation pollution — HR-шаблоны очищены от aviation-токенов, восстановлена релевантность HR-запросов.
- **Sprint 5:** Content enrichment — добавлены определения controlled zone, AWB/MAWB/HAWB, ULD, GHA, cutoff, dangerous goods в ключевые файлы.
- **Fix #1:** Добавлен внешний нормативный источник (ТК РФ гл. 11) с YAML frontmatter (`source_url`, `effective_date`).

### 10.3. Chunking
- **Token-based** (tiktoken cl100k_base, 500 токенов, overlap 75).
- Решает проблему `text.split()` на bulk-выгрузках без пробелов.
- 52 документа MVP → 583 чанка.

---

## 11. Известные проблемы и риски (приоритизированные)

### 🔴 High (блокируют production)

| # | Проблема | Влияние | Путь решения | Effort |
|---|---|---|---|---|
| 14 | **n8n coupling:** бизнес-логика в JS Code nodes | Сложность изменений, re-import workflow при правке copy | Extract в FastAPI: `/auth/check`, `/commands`, `/help`, `/start` | ~1 день |
| 7 | **Mistral free tier 429** | Rate-limit, задержки ответов, refusal на хороших вопросах | Переход на paid tier (Mistral Small/Pro) | $ |

### 🟡 Medium (влияют на demo stability / DX)

| # | Проблема | Влияние | Путь решения | Effort |
|---|---|---|---|---|
| 10 | **Cloudflare ephemeral tunnel** | URL меняется при рестарте → TG webhook dead | Named tunnel или собственный домен/VPS | ~2 часа |
| 2 | **TG webhook secret in-memory** | Невозможен автономный E2E POST на webhook | Использовать Bot API direct для smoke; ждать upstream n8n | n/a |
| 9 | **rag-api rebuild requirement** | Медленный цикл разработки (build при каждом изменении .py) | Добавить volume mount + `--reload` для dev | ~30 мин |

### 🟢 Low (accept / workaround)

| # | Проблема | Workaround |
|---|---|---|
| 13 | Intermittent 12-минутная задержка (1 раз) | Мониторинг latency в `/metrics` |
| 8 | n8n CLI path mangling на Windows | `MSYS_NO_PATHCONV=1` |
| 15 | Postgres binding blocked на Windows Docker | `expose-only` (без `ports:`) |
| 12 | n8n editor требует логин | Использовать CLI/SQL для отладки |

---

## 12. Сравнение с Требованиями (ТЗ)

| Требование ТЗ | Статус | Комментарий |
|---|---|---|
| Векторная БД (Supabase/pgvector) | ✅ | Postgres + pgvector, ivfflat index |
| Чанки по 500 токенов | ✅ | tiktoken cl100k_base, 500 токенов, overlap 75 |
| Мета: файл, раздел, дата | ✅ | + source_url, document_type, version, effective_from/to, status |
| Внешний источник (юр/HR) | ✅ | `external_tk_rf_chapter_11.md` (ТК РФ гл. 11) |
| Hybrid retrieval | ✅ | BM25 + vector + section rerank + coverage |
| Ответы с источниками | ✅ | Source.file, section, score, version, effective_date |
| Confidence threshold / refusal | ✅ | MIN_CONFIDENCE=0.25, `is_pure_refusal()`, `derive_status()` |
| Telegram-бот | ✅ | n8n workflow, whitelist, inline keyboard |
| Логирование и оценки | ✅ | request_logs, answer_feedback, review_queue |
| Черновики документов | ✅ | `HR_ORDER_HIRING` через кодовый шаблон (не LLM) |

**Все обязательные пункты MVP ТЗ выполнены.** Fix #1 и Fix #2 из `to_fix.md` закрыты 2026-05-17.

---

## 13. Рекомендации по приоритетам

### Сделать в ближайшую сессию (Sprint 6, ~1–2 дня)
1. **Extract business logic из n8n в FastAPI**
   - `POST /auth/check` — whitelist по telegram_user_id
   - `GET /commands` — routing для /help, /clear, /history, /docs
   - `GET /help`, `/start` — copy ответов
   - После: `N8N_BLOCK_ENV_ACCESS_IN_NODE=true`
2. **N2 Quick-actions:** «Уточнить» (rerun с top_k=10) и «Развернуть» (полный chunk).
3. **Dev-experience:** volume mount `./rag-api/app:/app/app:ro` + `uvicorn --reload` для локальной разработки.

### Сделать до production-deploy
4. **Mistral paid tier:** Устранит 429 и снизит latency.
5. **HTTPS / TLS termination:** Reverse proxy (Traefik / Nginx) с Let's Encrypt.
6. **Rate limiting на /ask:** Token bucket или retry-after honoring для Mistral.
7. **Named Cloudflare tunnel:** Стабильный webhook URL.

### Технический долг / архитектурные улучшения
8. **Cross-encoder reranker** (BGE-Reranker-v2-m3) на top-20 → top-5 для precision.
9. **Structure-aware chunking:** Split по markdown headers вместо фиксированных 500 токенов.
10. **SSO + Postgres RLS:** Ролевая модель для HR vs Legal.
11. **Langfuse / RAGAS:** Observability и auto-eval drift detection.

---

## 14. Заключение

TestRag — это **зрелый, хорошо протестированный и документированный MVP** с чёткой архитектурой и систематическим подходом к улучшению качества retrieval.

**Сильные стороны:**
- Высокие метрики retrieval (MRR 0.78, refusal 1.00) на golden set.
- 131 passing unit-test + eval regression gate + OpenAPI contract gate.
- Отличная документация (ADR, runbook, findings, known-issues).
- Graceful degrade при недоступности LLM.
- Безопасная конфигурация (secrets в env, postgres expose-only, path traversal защита).

**Критические пути до production:**
1. Extract бизнес-логики из n8n (Issue #14).
2. Переход на paid-tier Mistral (Issue #7).
3. Стабилизация webhook URL (Issue #10).

**Рекомендация:** Проект готов для демонстрации заказчику. Для production-deployment требуется Sprint 6 (extract) + инфраструктурные доработки (TLS, rate limiting, paid LLM).

---

*Аудит подготовлен автоматически на основе анализа исходного кода, тестов, документации и метрик проекта TestRag.*
