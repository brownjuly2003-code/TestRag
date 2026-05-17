# Next Session — TestRag

## Как начать новую сессию

Скопируй в новый чат с Claude:

```text
Продолжаем D:\TestRag.

Состояние HEAD `50699fe` (2026-05-17, Sprint 6 #1/#6/#7 closed + overlap rollback к ТЗ).

Свежие коммиты:
- `50699fe` feat(api): Sprint 6 #7 — Prev-N-QA retrieval augmentation (infrastructure)
- `217b84f` feat(api+bot): Sprint 6 #6 — N2 Quick-actions «🔁 Уточнить» / «📖 Развернуть»
- `2e74a17` feat(api): Sprint 6 #1 — extract whitelist/routing/help из n8n в rag-api
- `f98400b` fix(chunking): rollback chunk_overlap 75→50 (ТЗ literal compliance)
- `116b67f` feat(corpus): внешний нормативный источник + frontmatter parsing (Fix #1)

Тесты: pytest 192/192 зелёные (`python -m pytest -p no:schemathesis`).
Eval baseline: на overlap=75 — MRR=0.78 Hit@1=0.67 Hit@5=1.00 refusal=1.00.
**Eval-replay при overlap=50 — отложен**, см. ниже «Что не закрыто».

Корпус: MVP-48 (+external_tk_rf_chapter_11.md), chunk_count=583, documents=52.

Стек:
- FastAPI hybrid retrieval (token splitter cl100k_base 500/50, BM25 + vector + section rerank + frontmatter-driven metadata, `/ask?debug=true`).
- Mistral (singleton httpx).
- n8n 32 узла (pin 1.103.2). Whitelist Code node теперь — тонкий HttpRequest proxy на /tg/classify. N8N_BLOCK_ENV_ACCESS_IN_NODE=true.
- Telegram @AIagentJu_bot через cloudflared tunnel.

Что закрыто за session 2026-05-17:
- ✅ chunk_overlap 75→50 (буква ТЗ).
- ✅ Sprint 6 #1 (extract whitelist/routing/help): tg_classifier.py, tg_copy.py, /tg/classify, /tg/copy/{key}; N8N_BLOCK_ENV_ACCESS_IN_NODE=true; +32 unit-теста.
- ✅ Sprint 6 #6 (N2 Quick-actions): /clarify (rerun top_k=10), /expand (full chunk); Format Answer +row 3 (🔁 / 📖); n8n workflow +Clarify?/Expand? branches; +14 тестов.
- ✅ Sprint 6 #7 (Prev-N-QA infrastructure): multiturn.py + AskRequest.prev_qa_count opt-in (0..5), filter_relevant_prev_qas (skip refusal/low-conf); scripts/eval_multiturn.py (5 multi-turn cases, A/B harness); +15 тестов.

Что НЕ закрыто (defer на сессию с поднятым Docker — см. docs/known-issues.md #16):
- ⏸ Live eval replay при overlap=50 → обновить eval/baseline.json.
- ⏸ Live Prev-N-QA A/B (Sprint 6 #7) → вписать ΔHit@1 в docs/findings/2026-05-17-prev-n-qa-ablation.md.
- ⏸ Live TG smoke E2E с 🔁 Уточнить / 📖 Развернуть кнопками (scripts/smoke_tg_e2e.py пока проверяет только 📎/👍/👎/🧑‍💼).
- ⏸ n8n workflow import после Sprint 6 #1/#6 правок: `MSYS_NO_PATHCONV=1 docker compose exec -T n8n n8n import:workflow --input=/workflows/hr-legal-rag-workflow.json --projectId=AAx39VT08WENfUYU` + activate через SQL + `docker compose restart n8n`.

Перед работой:
- Не выводить .env, токены, ключи в чат.
- Docker Desktop поднимается 5-10 минут на холодную (Win11+WSL2, см. docs/known-issues.md #16). Запускать pre-warm параллельно с unit-работой, не блокироваться ожиданием.
- После изменений python-кода: `docker compose build rag-api && docker compose up -d --force-recreate rag-api` (issue 9).
- После изменений n8n workflow: import + activate (см. выше).
```

## Когда Docker поднимется — first thing to run

```powershell
cd D:\TestRag

# 0. Sanity: контейнеры up + healthcheck зелёные
docker compose up -d
docker ps --format "table {{.Names}}\t{{.Status}}"
curl http://localhost:8000/health

# 1. Eval replay при overlap=50 (закрывает task #9 from session 2026-05-17)
docker compose up -d --force-recreate rag-api
python scripts/eval_retrieval.py --output eval/baseline.json
cat eval/baseline.json | python -c "import sys,json; r=json.load(sys.stdin); print(r['summary'])"
# Если floor проходит (MRR≥0.60, Hit@1≥0.50, refusal≥0.85) — git commit eval/baseline.json.
# Если просел — diff с .tmp/baseline_overlap75.json, решить: оставить 50 (ТЗ) или вернуть 75 с обоснованием.

# 2. Prev-N-QA A/B (Sprint 6 #7 live)
python scripts/eval_multiturn.py --output .tmp/eval_multiturn.json
# Вписать ΔHit@1/ΔHit@5/ΔMRR в docs/findings/2026-05-17-prev-n-qa-ablation.md § «A/B harness».

# 3. n8n workflow import после Sprint 6 #1/#6 правок
MSYS_NO_PATHCONV=1 docker compose exec -T n8n n8n import:workflow --input=/workflows/hr-legal-rag-workflow.json --projectId=AAx39VT08WENfUYU
docker compose exec -T postgres psql -U testrag -d testrag -c "update n8n.workflow_entity set active=true where name='TestRag HR Legal Assistant';"
docker compose restart n8n

# 4. Cloudflare tunnel — пересоздать если URL мёртвый (см. docs/demo-runbook.md)
docker logs testrag-cloudflared --tail=5  # ищет 'Registered tunnel connection'

# 5. TG E2E smoke — поправить scripts/smoke_tg_e2e.py для новых кнопок 🔁/📖
python scripts/smoke_tg_e2e.py
```

## Минимальные команды (без Docker)

```powershell
cd D:\TestRag

# Pytest gate (быстрый, без живого API):
python -m pytest -p no:schemathesis  # 192 passed

# OpenAPI contract gate (ловит schema drift):
python -m pytest -p no:schemathesis rag-api/tests/test_openapi_contract.py  # 4 passed
# При расхождении: python scripts/export_openapi.py → commit docs/openapi.yaml.
```

## Стек контейнеров (после Sprint 6 #1)

| Контейнер | Image | Status check | Внешний порт | Прим. |
|---|---|---|---|---|
| `testrag-postgres-1` | `pgvector/pgvector:pg16` | pg_isready healthcheck | **expose only**, без publish | — |
| `testrag-rag-api-1` | local build | urllib /health (timeout=3) | `8000:8000` | +ALLOWED_TELEGRAM_USER_IDS env |
| `testrag-n8n-1` | `n8nio/n8n:1.103.2` (pinned) | n8n healthz | `5678:5678` | **N8N_BLOCK_ENV_ACCESS_IN_NODE=true** (Sprint 6 #1) |
| `testrag-cloudflared` | cloudflare/cloudflared | runtime registration | none (outbound only) | — |

POSTGRES_PASSWORD и N8N_ENCRYPTION_KEY теперь `${VAR:?required}` — `docker compose up` упадёт если не указано в `.env`.

## Где что лежит (актуализировано session 2026-05-17)

- **Корпус** — `corpus/*.md` (200 файлов + external_tk_rf_chapter_11.md, 7 категорий + федеральный закон). MVP — `manifests/MVP_CORPUS_FILES.txt` (48 файлов).
- **rag-api** — `rag-api/app/{main,rag,storage,llm,settings,tg_classifier,tg_copy,multiturn,prompts}.py`.
- **Тесты** — `rag-api/tests/test_{api,rag,llm,n8n_workflow,openapi_contract,ingestion,tg_classifier,multiturn}.py` (192/192).
- **n8n workflow** — `n8n/workflows/hr-legal-rag-workflow.json` (32 узла).
- **Eval** — `scripts/eval_retrieval.py` (10 single-turn golden Qs), `scripts/eval_multiturn.py` (5 multi-turn cases A/B), `scripts/test_eval_regression.py` (pytest gate), `eval/baseline.json` (closed, overlap=75; replay при overlap=50 deferred).
- **Cross-audit** — `kimi_audit_17_05_26.md` (Kimi полный аудит).
- **Findings** — `docs/findings/2026-05-17-{sprint4-retrieval-polish,prev-n-qa-ablation}.md`.
- **Known issues** — `docs/known-issues.md` (16 issues, #14 RESOLVED, #16 NEW Docker cold start).
- **ADR** — `docs/adr/0001-orchestrator-n8n.md`, `0002-bm25-plus-pgvector-hybrid.md`, `0003-mistral-llm.md`.
- **OpenAPI** — `docs/openapi.yaml/.json` (12 paths, 23 schemas; gate в test_openapi_contract.py).
