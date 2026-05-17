# Next Session — TestRag

## Как начать новую сессию

Скопируй в новый чат с Claude:

```text
Продолжаем D:\TestRag.

Состояние HEAD `74f45fd` (2026-05-17 night):
- Sprint 4 retrieval polish + BCG demo bar + Sprint 5 cross-audit hardening — DONE.
- pytest 112/112. Eval CI gate `pytest scripts/test_eval_regression.py` зелёный.
- 10 golden Qs: MRR=0.76 Hit@1=0.67 Hit@5=0.89 refusal=1.00 avg_conf=0.85.
- Корпус: MVP-47, chunk_count=189, documents=51.
- Стек: FastAPI hybrid retrieval (BM25 + vector + section rerank, weights env) → Mistral → n8n (28 узлов, pin 1.103.2) → Telegram @AIagentJu_bot через cloudflared tunnel (URL ephemeral).
- Sprint 5 закрыл P0/P1 из Kimi+Codex cross-audit: content enrichment glossary, eval CI gate, compose hardening (mandatory secrets, healthchecks, postgres expose-only), LLM guards (choice/JSON/dim mismatch), env-параметризованные hybrid weights.

Документация:
- README.md — value-prop + retrieval metrics table.
- mvp-plan.md — Sprint 4-5 done, Sprint 6 backlog.
- docs/findings/2026-05-17-sprint4-retrieval-polish.md — детальный анализ.
- .tmp/kimi-audit.md (185 строк) + .tmp/codex-audit.md (149 строк) — cross-audit, основание Sprint 5.
- docs/next-session.md (этот файл).

Sprint 6 backlog (если хочется продолжать):
1. **Extract business logic из n8n** в FastAPI endpoints (whitelist, command routing, /help copy). После — N8N_BLOCK_ENV_ACCESS=true. ~1 день.
2. **OpenAPI export** в docs/openapi.yaml + ADR. ~4 часа.
3. **Retrieval explainability** debug-поля в /ask (coverage, section_boost). ~2 часа.
4. **Empty-query fallback** на vector-only когда BM25 tokens=[]. ~1 час.
5. **HTTP client pooling** (singleton на runtime startup). ~2 часа.
6. **N2 Quick-actions** «Уточнить» / «Развернуть». ~3 часа.

Перед работой:
- Не выводить .env, токены, ключи в чат.
- После изменений python-кода: `docker compose build rag-api && docker compose up -d --force-recreate rag-api` (см. issue 9 в docs/known-issues.md).
- После изменений n8n workflow: `MSYS_NO_PATHCONV=1 docker compose exec -T n8n n8n import:workflow --input=/workflows/hr-legal-rag-workflow.json --projectId=AAx39VT08WENfUYU` + activate через SQL + `docker compose restart n8n`.
- Перед TG-смоком: убедиться что cloudflare tunnel жив (`docker logs testrag-cloudflared --tail=5` ищет `Registered tunnel connection`).
```

## Минимальные команды

```powershell
cd D:\TestRag

# Pytest gate (быстрый, без живого API):
python -m pytest -p no:schemathesis  # 112 passed

# Eval CI regression gate (требует rag-api up, ~1.5 минуты):
python -m pytest -p no:schemathesis scripts/test_eval_regression.py  # 7 passed

# Поднять стек (postgres expose-only, rag-api healthcheck, n8n 1.103.2):
docker compose up -d

# Здоровье:
curl http://localhost:8000/health    # chunk_count=189
curl http://localhost:5678/healthz   # n8n
docker ps --format "table {{.Names}}\t{{.Status}}"

# Eval baseline run/update:
python scripts/eval_retrieval.py --output eval/baseline.json
cat eval/baseline.json | python -c "import sys,json; r=json.load(sys.stdin); print(r['summary'])"

# /metrics observability:
curl 'http://localhost:8000/metrics?window_hours=168'

# /docs корпус summary с sample_files:
curl http://localhost:8000/docs/summary | python -m json.tool

# History live:
curl 'http://localhost:8000/history?telegram_user_id=432751211&limit=5'

# TG E2E smoke (user account через Telethon, нажимает 📎/👎/🧑‍💼):
python scripts/smoke_tg_e2e.py       # читает D:/MCP/telegram-mcp/.env
```

## Стек контейнеров (Sprint 5 hardened)

| Контейнер | Image | Status check | Внешний порт |
|---|---|---|---|
| `testrag-postgres-1` | `pgvector/pgvector:pg16` | pg_isready healthcheck | **expose only**, без publish |
| `testrag-rag-api-1` | local build | urllib /health (urllib timeout=3) | `8000:8000` |
| `testrag-n8n-1` | `n8nio/n8n:1.103.2` (pinned) | n8n healthz | `5678:5678` |
| `testrag-cloudflared` | cloudflare/cloudflared | runtime registration | none (outbound only) |

POSTGRES_PASSWORD и N8N_ENCRYPTION_KEY теперь `${VAR:?required}` — `docker compose up` упадёт если не указано в `.env`.

## Sprint 5 schema check

```powershell
# Корпус (51 docs, 189 chunks):
docker compose exec -T postgres psql -U testrag -d testrag -tA -c "select count(distinct id), count(*) from documents d join document_chunks c on c.document_id=d.id;"

# Sample_files в /docs:
docker compose exec -T postgres psql -U testrag -d testrag -tA -c "
with categorized as (
    select distinct d.id, d.file_name,
        case when file_name ~ '^[0-9]+_hr_pol' then '01_hr_pol' else 'other' end as cat
    from documents d join document_chunks c on c.document_id=d.id
) select cat, count(*) from categorized group by 1 order by 1;
"

# Hybrid weights в runtime:
docker compose exec -T rag-api python -c "from app.rag import HybridRetriever as R; print('bm25=',R.BM25_WEIGHT,'vec=',R.VECTOR_WEIGHT,'cov_exp=',R.COVERAGE_EXP,'sect=',R.SECTION_BOOST_MAX)"
```

## TG E2E через telegram-mcp / Telethon

Установлен `chigwell/telegram-mcp` в `D:/MCP/telegram-mcp/`. Сессия — StringSession для @AIagentJu_bot whitelist (id=432751211, имя Julia).

`scripts/smoke_tg_e2e.py` гоняет:
1. send_message «Что такое controlled zone?»
2. wait reply → verify N4 `reply_to_msg_id` == user msg_id ✓
3. inspect inline_keyboard → 2 📎 follow-up + 2 👍/👎 ✓
4. click первой 📎 → wait second reply (N1)
5. click 👎 → edit reply markup → 3 reason buttons
6. click 🧑‍💼 → wait ACK «Ваш запрос направлен HR/Legal на ручную обработку» (N3)
7. select review_queue order by created_at desc → `human|5`

## Если cloudflare tunnel умер

`docker logs testrag-cloudflared` пусто или контейнер не запущен → URLs эфемерные. Процедура восстановления — `docs/demo-runbook.md` раздел «Локальный Telegram Webhook».

## Где что лежит

- **Корпус** — `corpus/*.md` (200 файлов, 7 категорий). MVP подмножество — `manifests/MVP_CORPUS_FILES.txt` (47 файлов).
- **rag-api** — `rag-api/app/{main,rag,storage,llm,prompts}.py`. Тесты — `rag-api/tests/`.
- **n8n workflow** — `n8n/workflows/hr-legal-rag-workflow.json` (28 узлов).
- **Eval** — `scripts/eval_retrieval.py` (10 golden Qs) + `scripts/test_eval_regression.py` (pytest gate) + `eval/baseline.json` (закоммичен).
- **Cross-audit (Kimi+Codex)** — `.tmp/kimi-audit.md` (185 строк) + `.tmp/codex-audit.md` (149 строк). Обновлены 2026-05-17 night.
- **Findings** — `docs/findings/2026-05-17-sprint4-retrieval-polish.md`.
- **Research** — `docs/research/{kimi,codex}-bot-ux.md` + `SYNTHESIS.md` (Sprint 1-3 roadmap).
- **Known issues** — `docs/known-issues.md`.
