# Next Session — TestRag

## Как начать новую сессию

Скопируй в новый чат с Claude:

```text
Продолжаем D:\TestRag.

HEAD будет на свежем коммите EOS-сессии 2026-05-17 (eval-driven overlap correction + Sprint 6 #1 partial workaround + live TG E2E confirmed).

Базовые цифры:
- pytest: 192/192 зелёные.
- Eval baseline на overlap=75 + MIN_CONFIDENCE=0.25: MRR 0.78 / Hit@1 0.67 / Hit@5 1.00 / refusal 1.0 / avg_conf 0.80.
- Live TG E2E (scripts/smoke_tg_e2e.py): 5/6 чеков ✓ (N1 follow-up, N2 🔁 clarify, N2 buttons present, N3 handover ack, N4 reply threading; единственный minor — 📖 expand timeout, race с clarify reply).

Корпус: MVP-48 (+external_tk_rf_chapter_11.md), chunk_count=583, documents=52.

Стек:
- FastAPI hybrid retrieval (token splitter cl100k_base 500/75, BM25 + vector + section rerank + frontmatter-driven metadata, `/ask?debug=true`).
- Mistral (singleton httpx).
- n8n 32 узла (pin 1.103.2, см. known-issues #17 про CLI workaround). Sprint 6 #1 ПОКА PARTIAL — HTTP nodes ещё читают $env (issue #18), N8N_BLOCK_ENV_ACCESS_IN_NODE=false override через .env.
- Telegram @AIagentJu_bot через cloudflared tunnel (testrag-cloudflared, ephemeral trycloudflare).

Что закрыто 2026-05-17 EOS (full day):
- ✅ Live eval replay overlap=50 → регрессия → rollback к overlap=75 (eval-driven, ADR-0004). MIN_CONFIDENCE override drift 0.35→0.25 (issue #19).
- ✅ Prev-N-QA live A/B на финальном overlap=75 baseline: ΔHit@1=0 ΔHit@5=+0.20 ΔMRR=+0.05. Решение: opt-in (default=0).
- ✅ n8n workflow import после Sprint 6 #1/#6 правок — через SQL UPDATE workaround (CLI 1.103.2 broken, issue #17). Workflow active=true, 32 nodes.
- ✅ scripts/smoke_tg_e2e.py расширен под N2 🔁/📖, прогнан live, 5/6 ✓.
- ✅ Schema fix: ALTER TABLE n8n."user" ADD COLUMN role GENERATED ALWAYS AS ("roleSlug") STORED.
- ✅ docs/known-issues.md +#17/#18/#19, docs/adr/0004-chunk-overlap-75.md, docs/findings/2026-05-17-overlap-50-regression.md.

Что НЕ закрыто (на следующую сессию):
- ⏸ Sprint 6 #1 finish (issue #18): refactor 4 TG HTTP nodes на `authentication: predefinedCredentialType, nodeCredentialType: 'telegramApi'` (НЕ через $credentials.X expression — не работает, попытка дала пустой токен → 404). После refactor вернуть `N8N_BLOCK_ENV_ACCESS_IN_NODE=true` default.
- ⏸ Sprint 6 #2 OpenAPI dump (если есть). #3-#5 closed (`881c5f2`, `470b692`, `b7812b9`).
- ⏸ Investigate `📖 Развернуть expand` race в TG smoke (single failure из 6). Возможно scripts/smoke_tg_e2e.py не дожидается reply2.id refresh после clarify click.
- ⏸ n8n upgrade за пределы 1.103.2 (issue #17) с regression-тестом workflow.

Перед работой:
- Не выводить .env, токены, ключи в чат.
- Docker Desktop поднимается 5-10 минут на холодную (issue #16). Pre-warm параллельно с unit-работой.
- После изменений n8n workflow: SQL UPDATE workaround (`.tmp/patch_workflow.py` + docker cp + `MSYS_NO_PATHCONV=1 docker exec ... psql -f //tmp/update_workflow.sql` + restart).
- Cloudflared tunnel ephemeral: при рестарте `docker rm -f testrag-cloudflared` → новый run → update N8N_WEBHOOK_URL в .env → `docker compose up -d --force-recreate n8n` → `deleteWebhook + activate workflow` (n8n сам setWebhook с правильным secret).
```

## Когда нужно поднять окружение с нуля

```bash
cd D:/TestRag

# 0. Sanity
docker compose up -d
docker ps --format "table {{.Names}}\t{{.Status}}"
curl http://localhost:8000/health   # chunk_count=583 expected

# 1. Cloudflared tunnel (ephemeral — нужно при каждом session start)
docker rm -f testrag-cloudflared 2>/dev/null
docker run -d --name testrag-cloudflared --network testrag_default cloudflare/cloudflared:latest tunnel --no-autoupdate --url http://n8n:5678
sleep 15
TUNNEL=$(docker logs testrag-cloudflared 2>&1 | grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' | head -1)
echo "tunnel: $TUNNEL"

# 2. Update N8N_WEBHOOK_URL in .env
python -c "
import pathlib, re
p = pathlib.Path('.env')
text = p.read_text(encoding='utf-8')
new = re.sub(r'^N8N_WEBHOOK_URL=.*$', f'N8N_WEBHOOK_URL=$TUNNEL/', text, flags=re.MULTILINE)
p.write_text(new, encoding='utf-8')
"
docker compose up -d --force-recreate n8n

# 3. Reset TG webhook + reactivate workflow (n8n auto-setWebhook with secret)
python -c "
import pathlib, re, urllib.request
token = re.search(r'TELEGRAM_BOT_TOKEN=(\S+)', pathlib.Path('.env').read_text(encoding='utf-8')).group(1)
urllib.request.urlopen(urllib.request.Request(f'https://api.telegram.org/bot{token}/deleteWebhook', data=b'')).read()
print('webhook deleted')
"
docker compose exec -T postgres psql -U testrag -d testrag -c "UPDATE n8n.workflow_entity SET active=false WHERE id='testrag-hr-legal-assistant'; UPDATE n8n.workflow_entity SET active=true WHERE id='testrag-hr-legal-assistant';"
docker compose restart n8n
sleep 15
# verify
python -c "
import pathlib, re, urllib.request, json
token = re.search(r'TELEGRAM_BOT_TOKEN=(\S+)', pathlib.Path('.env').read_text(encoding='utf-8')).group(1)
with urllib.request.urlopen(f'https://api.telegram.org/bot{token}/getWebhookInfo', timeout=20) as r:
    info = json.loads(r.read())['result']
print('host:', info.get('url','').split('/')[2])
print('pending:', info.get('pending_update_count'))
print('last_error:', info.get('last_error_message'))
"

# 4. Eval gates
python scripts/eval_retrieval.py --output eval/baseline.json
python scripts/eval_multiturn.py --output .tmp/eval_multiturn.json
python scripts/smoke_tg_e2e.py
```

## Минимальные команды (без Docker)

```powershell
cd D:\TestRag

# Pytest gate (быстрый, без живого API):
python -m pytest -p no:schemathesis  # 192 passed

# OpenAPI contract gate (ловит schema drift):
python -m pytest -p no:schemathesis rag-api/tests/test_openapi_contract.py  # 4 passed
```

## Стек контейнеров

| Контейнер | Image | Status check | Внешний порт | Прим. |
|---|---|---|---|---|
| `testrag-postgres-1` | `pgvector/pgvector:pg16` | pg_isready healthcheck | **expose only** | + alias column `n8n.user.role` (workaround #17) |
| `testrag-rag-api-1` | local build | urllib /health (timeout=3) | `8000:8000` | overlap=75, min_conf=0.25 |
| `testrag-n8n-1` | `n8nio/n8n:1.103.2` (pinned) | n8n healthz | `5678:5678` | `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` через .env (issue #18) |
| `testrag-cloudflared` | cloudflare/cloudflared | runtime registration | none (outbound only) | ephemeral, пересоздавать при рестарте |

POSTGRES_PASSWORD и N8N_ENCRYPTION_KEY — `${VAR:?required}`.

## Где что лежит (актуализировано 2026-05-17 EOS)

- **Корпус** — `corpus/*.md` (200 файлов + external_tk_rf_chapter_11.md). MVP — `manifests/MVP_CORPUS_FILES.txt` (48 файлов).
- **rag-api** — `rag-api/app/{main,rag,storage,llm,settings,tg_classifier,tg_copy,multiturn,prompts}.py`.
- **Тесты** — `rag-api/tests/test_{api,rag,llm,n8n_workflow,openapi_contract,ingestion,tg_classifier,multiturn}.py` (192/192).
- **n8n workflow** — `n8n/workflows/hr-legal-rag-workflow.json` (32 узла).
- **Eval** — `scripts/eval_retrieval.py` (10 single-turn golden Qs), `scripts/eval_multiturn.py` (5 multi-turn A/B), `scripts/test_eval_regression.py` (pytest gate), `eval/baseline.json` (overlap=75 + min_conf=0.25 closed).
- **Smoke** — `scripts/smoke_tg_e2e.py` (N1/N2/N3/N4 buttons), `scripts/smoke_followup.py`.
- **Cross-audit** — `kimi_audit_17_05_26.md` (Kimi полный аудит).
- **Findings** — `docs/findings/2026-05-17-{sprint4-retrieval-polish,prev-n-qa-ablation,overlap-50-regression}.md`.
- **Known issues** — `docs/known-issues.md` (19 issues, #14/#16 RESOLVED/known, #17/#18/#19 NEW).
- **ADR** — `docs/adr/0001-n8n-as-bot-orchestrator.md`, `0002-in-memory-bm25-hybrid-retriever.md`, `0003-mistral-as-llm-and-embeddings.md`, `0004-chunk-overlap-75.md`.
- **OpenAPI** — `docs/openapi.yaml/.json` (12 paths, 23 schemas).
- **Workflow patch scripts** — `.tmp/patch_workflow.py`, `.tmp/find_env_refs.py`, `.tmp/update_workflow.sql` (gitignored).
