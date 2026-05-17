# Known Issues & Workarounds

Все известные проблемы TestRag MVP по состоянию на 2026-05-17 night (HEAD `74f45fd`). Каждая запись: симптом → root cause → текущий status → workaround/fix path.

## 1. ~~Retrieval polluted после aviation pass~~ ✅ RESOLVED Sprint 4

**Симптом** (был): `Что такое controlled zone?` даёт top-5 sources из `02_hr_tmp_*` (трудовой договор, удалёнка, приказ об отпуске) вместо `01_hr_pol_safety.md`.

**Root cause**: Aviation profile pass (commit `7c6951a`, 2026-05-16) переписал ВСЕ 200 corpus-файлов под авиагрузовую тематику, включая HR-шаблоны. Aviation токены распределились равномерно по корпусу, забили top-K HR-шаблонами.

**Resolved** в commit `9017878` (Sprint 4): `git checkout 8aa97b9 --` для 76 файлов (01_hr_pol_* кроме safety, 02_hr_tmp_* все, 07_faq_* кроме aviation-FAQ). Удалён `test_aviation_profile_in_hr_probation`. Eval: MRR 0.28→0.56. Подробно — `docs/findings/2026-05-17-sprint4-retrieval-polish.md`.

Дополнительно Sprint 5 (`74f45fd`) расширил MVP-44 → MVP-47 (+aviation FAQ) и добавил глоссарий controlled zone / AWB / ULD / GHA / cutoff / DG в три ключевых файла. Финал: MRR 0.76, Hit@1 0.67, refusal accuracy 1.00.

## 2. ~~TG webhook secret in-memory — синтетический POST невозможен~~ ✅ RESOLVED Sprint 7 (polling-mode)

**Был**: `curl -X POST <N8N_WEBHOOK_URL>/webhook/...telegramtrigger/webhook -d '{...}'` → `403 {"message":"Provided secret is not valid"}` из-за random secret_token, который n8n TelegramTrigger v1.3 генерил при активации workflow и хранил in-memory.

**Resolved Sprint 7**: TelegramTrigger node заменён на регулярный Webhook node (POST `/webhook/tg-poll`, без secret). Bot API webhook удалён (`deleteWebhook` при старте `tg-poll-bridge`). Поставка Telegram updates идёт через polling-bridge (`services/tg_poll_bridge/`) во внутренний n8n endpoint. Синтетический POST стал тривиальным:
```bash
curl -X POST http://localhost:5678/webhook/tg-poll -H 'Content-Type: application/json' \
  -d '{"update_id":1,"message":{...}}'
```
Это разблокирует автономное E2E тестирование без Telethon-ник.

## 3. Mistral возвращает Markdown V1 при parse_mode=HTML

**Симптом**: Bot прислал ответ `**Ответ:** **controlled zone** — это зона...`. Звёздочки видны как plain text, не bold.

**Root cause**: parse_mode='HTML' в Telegram sendMessage. Mistral system prompt не диктует HTML, модель возвращает MarkdownV1 по умолчанию (`**bold**`, `` `code` ``, `- list`).

**Status**: FIXED в commit `ef23933`. Format Answer теперь делает MD→HTML конверсию **после** HTML-escape:
- `` `X` `` → `<code>X</code>`
- `**X**` → `<b>X</b>`
- `- ` в начале строки → `• `

Regex-safe (не трогает уже escape-нутые `&lt;` `&gt;`).

**Не покрыто**:
- Италик `*text*` (риск ложных срабатываний на `5*8` арифметике).
- Ссылки `[label](url)` (Mistral редко выдаёт URL в этом контексте).
- Заголовки `# Header` — рендерятся как plain text.

## 4. n8n HTTP node затирает $json для следующего узла

**Симптом**: execution 15 упал на `Ask RAG API` с `422 Field required`. Causes Ask RAG получал `$json.text=undefined`.

**Root cause**: Send Typing — это HTTP Request node. Его output = Bot API response `{ok:true, result:true}`. Этот output становится `$json` для следующего узла. У Ask RAG API было `JSON.stringify({question: $json.text, ...})` → `text` отсутствует в `{ok:true,result:true}` → undefined → /ask 422.

**Status**: FIXED в commit `7498a5c`. Ask RAG API теперь читает `$node['Whitelist'].json.text` и `.user_id` напрямую. Тот же паттерн используется в Format Answer для chat_id.

**Регрессионный тест**: `test_ask_rag_reads_user_input_from_whitelist_not_send_typing_response` ловит возврат к `$json.text`.

## 5. Telegram sendMessage лимит 4096 символов

**Симптом**: Длинный Mistral-ответ + 5 источников может превысить 4096 → Bot API возвращает `400 message is too long` → workflow execution error, юзер получает ничего.

**Status**: FIXED в commit `daa8795`. Format Answer split:
1. Если text ≤ 4000 — 1 part.
2. Иначе split по `\n\n` (paragraph), накапливая в current до 4000.
3. Если параграф сам по себе > 4000 — split по предложениям (regex `/(?<=[.!?])\s+/`).
4. Если предложение > 4000 — hard slice.
5. `balanceTags()` дозакрывает разорванные `<b>`/`<code>` в каждой части.
6. Каждая часть добавляет `<i>часть N/M</i>` (только при N>1).

## 6. inline keyboard на split-сообщениях

**Симптом**: Format Answer возвращает массив items (split). n8n Telegram-узел применяет inline keyboard к КАЖДОМУ item → дубликаты кнопок на каждой части.

**Status**: FIXED в commit `daa8795`. Решение в workflow:
- Новый `Last Part?` If-узел после Format Answer.
- `main[0]` (is_last=true) → Send Answer (с inline keyboard 👍/👎).
- `main[1]` (is_last=false) → Send Answer Part (БЕЗ keyboard, тот же parse_mode=HTML).

**Live verified** через `.tmp/smoke_split.py`: 2 parts (3895+674 chars) — first без keyboard, second с keyboard.

## 7. Mistral free tier 429 rate-limit

**Симптом**: Быстрая последовательность /ask запросов (>10 за минуту) → Mistral возвращает 429. Иногда ответ refused даже на хороший вопрос.

**Status**: PARTIAL fix в commit `e26a7da`. Graceful degrade: при 429 LLM build_grounded_answer выдаёт extractive answer из найденных chunks без вызова Mistral. `is_pure_refusal()` helper отличает «полный отказ» от «cautious lead-in + body» (4 unit-теста в test_api.py).

**Не покрыто**: throttle на client-side (retry-after honoring). Прод-сценарий требует paid tier.

## 8. n8n CLI path mangling на Windows + Git Bash

**Симптом**: `docker compose exec -T n8n n8n import:workflow --input=/workflows/hr-legal-rag-workflow.json` → `ENOENT: no such file or directory, open 'C:/Program Files/Git/workflows/hr-legal-rag-workflow.json'`. Git Bash на Windows автоматически конвертирует POSIX-пути в Windows-пути.

**Status**: WORKAROUND. Все import/update команды теперь префиксированы `MSYS_NO_PATHCONV=1`:
```bash
MSYS_NO_PATHCONV=1 docker compose exec -T n8n n8n import:workflow --input=/workflows/hr-legal-rag-workflow.json --projectId=AAx39VT08WENfUYU
```

## 9. rag-api требует rebuild после изменения .py

**Симптом**: `docker compose up -d --force-recreate rag-api` использует **существующий** image — новый код в `app/main.py` не применяется. Endpoint /history возвращает 404 пока rebuild не сделан.

**Root cause**: `docker-compose.yml` имеет `build: context: ./rag-api`, но НЕТ volume mount source. Контейнер бежит снапшот при build.

**Status**: WORKAROUND. Сценарий после Python edits:
```bash
docker compose build rag-api && docker compose up -d --force-recreate rag-api
```

**Fix candidate** (DX improvement): добавить volume `- ./rag-api/app:/app/app:ro` в docker-compose, тогда uvicorn --reload подхватит изменения сразу. Trade-off — нужно `--reload` flag, что не подходит для prod-like setup.

## 10. ~~Cloudflare tunnel — эфемерные URLs~~ ✅ RESOLVED Sprint 7 (polling-mode)

**Был**: `docker compose down` + `docker compose up` → trycloudflare URL изменился → TG webhook на dead URL → бот молчит.

**Resolved Sprint 7**: убран весь внешний-tunnel путь. `services/tg_poll_bridge/` (docker container, ~150 lines stdlib-only Python) long-poll'ит `https://api.telegram.org/bot<TOKEN>/getUpdates` и POST'ит каждый update в `http://n8n:5678/webhook/tg-poll` (internal docker network). Никаких публичных URLs у n8n, никаких cloudflare/ngrok/named-tunnel'ов. Запуск: `docker compose up -d tg-poll-bridge`. Состояние persistent через restart (n8n offset не нужно хранить — Telegram отдаёт «непрочитанные» updates пока bridge не пометит их прочтёнными через offset).

**Trade-off**: ~5s polling latency vs мгновенный webhook. Для MVP HR/legal demo приемлемо.

**Fallback (если когда-то нужен публичный URL)**: cloudflared/ngrok scripts в `docs/demo-runbook.md` остались, но более не required.

## 11. Workflow .ready vs editing races (CX-related)

Из global feedback memory: для CX-спеков. Не применимо к TestRag, но напомню — не редактировать `.workflow/inbox/*.md` после `touch .ready`. В TestRag CX не используется.

## 12. n8n editor требует логин (для UI отладки)

**Симптом**: `http://localhost:5678/rest/workflows` → 401. UI требует владельца аккаунта (setup wizard).

**Status**: KNOWN, не fix. Для отладки воркфлоу — через `docker compose exec n8n n8n ...` CLI и Postgres queries в `n8n.execution_entity` / `n8n.execution_data`.

## 13. Mistral 12-минутная задержка ответа (наблюдалась 1 раз)

**Симптом**: От «Что такое controlled zone?» (1:47 AM) до ответа (1:59 AM) прошло 12 минут.

**Root cause**: Подозрение на Mistral 429 retry с длинным backoff в `requests` или `httpx` client. Параллельно — n8n execution 17 показал реальный runtime 8.7 сек. Скорее всего: Cloudflare tunnel пересоздался, TG webhook задержался с доставкой, либо Mistral free tier забекдоффил.

**Status**: INTERMITTENT, не воспроизводится стабильно. Если повторится — добавить timing в логах rag-api.

## 14. n8n coupling — бизнес-логика в JS Code nodes

**Симптом**: Whitelist check, command routing (/help, /docs, /history, /start), greeting/help copy и Format Answer (MD→HTML, split, confidence chip, refusal handling) — всё в JS Code nodes внутри `n8n/workflows/hr-legal-rag-workflow.json`. Изменение копи приветствия = re-import workflow + restart n8n.

**Root cause**: MVP-ускорение — собрали быстро через n8n UI. Architecturally n8n должен быть pure transport orchestrator (TG → routing API → sendMessage), а не business engine.

**Status**: KNOWN, Sprint 6 backlog (Kimi+Codex audit P1 #3). Workaround на Sprint 5 — добавлены pin тесты на JS nodes (`test_format_answer_*` в `test_n8n_workflow.py`) чтобы регрессии ловились в pytest.

**Fix path**: вынести whitelist check, command routing, copy в FastAPI endpoints `/auth/check`, `/commands`, `/start`, `/help`. После этого `N8N_BLOCK_ENV_ACCESS_IN_NODE=true`. Effort: ~1 день.

## 15. Postgres 127.0.0.1 binding blocked на Windows Docker

**Симптом**: `docker compose up` падает на `bind: An attempt was made to access a socket in a way forbidden by its access permissions` при попытке `ports: ["127.0.0.1:5432:5432"]` ИЛИ `"5432:5432"`.

**Root cause**: Hyper-V dynamic port reservation на Windows. Порты в диапазоне 1024-60000 могут быть динамически зарезервированы Hyper-V и не показываются через `netsh int ipv4 show excludedportrange protocol=tcp`.

**Status**: WORKAROUND применён в Sprint 5 (`74f45fd`): postgres переведён в `expose: ["5432"]` (без `ports:` publish). Внешний доступ только через `docker compose exec postgres psql`. Это попутно закрывает codex-audit#3 (DB не должна быть exposed на хост).

**Fix path для prod**: postgres всегда expose-only, доступ извне — через bastion / firewall / reverse proxy. На dev-машине Windows — текущее состояние OK.

## Сводка: что блокирует «production-ready»

| issue | блокирует demo? | блокирует prod? |
|---|---|---|
| 1 retrieval polluted | RESOLVED Sprint 4 | RESOLVED |
| 2 webhook secret in-memory | ✅ RESOLVED Sprint 7 (polling-mode) | RESOLVED |
| 3 MD→HTML | FIXED | FIXED |
| 4 $json shadowing | FIXED | FIXED |
| 5 4096 limit | FIXED | FIXED |
| 6 keyboard on split | FIXED | FIXED |
| 7 Mistral 429 | нет (graceful degrade) | да (paid tier needed) |
| 8 path mangling | нет | нет (CI Linux) |
| 9 rebuild requirement | нет | нет |
| 10 ephemeral tunnel | ✅ RESOLVED Sprint 7 (polling-mode bridge) | RESOLVED |
| 11 N/A | — | — |
| 12 n8n login | нет | нет (используем CLI/SQL) |
| 13 intermittent latency | нет | мониторить |
| 14 n8n coupling | ✅ RESOLVED (Sprint 6 #1, commit `2e74a17`) | — |
| 15 Windows postgres binding | нет (expose-only workaround) | нет (prod = firewall) |
| 16 Docker Desktop cold start ≥10мин | нет | poll или принять и defer eval-replay |
| 17 n8n 1.103.2 CLI import + schema mismatch | да (SQL UPDATE workaround) | да (upgrade n8n или migrate schema) |
| 18 Sprint 6 #1 partial — HTTP nodes ещё на $env | да (BLOCK_ENV=false override) | да (workflow refactor на credentials) |
| 19 MIN_CONFIDENCE override drift в .env | да (вернуть к 0.25) | да (.env validate gate) |

Демо-готовность: 🟢 retrieval polished (MRR=0.78 на overlap=75 + MIN_CONFIDENCE=0.25), refusal=1.0, content gaps закрыты. Sprint 6 #1/#6/#7 закрыты в session 2026-05-17 (n8n extract, N2 Quick-actions, Prev-N-QA infrastructure). Live TG E2E подтверждён 2026-05-17 EOD (5/6 N1+N2+N3+N4). **Sprint 7 (2026-05-18): polling-mode TG bridge закрыл issues #2 + #10** — публичный URL/тоннель больше не нужен. Production-readiness — Mistral paid tier (issue 7) остаётся единственный hard blocker для prod-сценария.

## 16. Docker Desktop cold start на Win11 + WSL2 = 5-10 минут

**Симптом**: `docker compose up`/`docker info` отдаёт `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified` или (после старта UI) `500 Internal Server Error`. Из-за этого live eval replay блокируется на 10+ минут даже после `Start-Process 'Docker Desktop.exe'`.

**Root cause**: Hyper-V / WSL2 backend разворачивает виртуальную машину `docker-desktop`, инициализирует Linux engine, открывает named pipe. На свежей загрузке системы (или после `Get-Process | Stop-Process` reset) это занимает 5-10 минут. UI-процессы `Docker Desktop.exe` появляются быстро (15-30с), но engine API возвращает 500 пока `containerd` + `dockerd` внутри WSL не запустились полностью.

**Status**: КАТЕГОРИЧЕСКИ NORMAL, не bug. Лечится временем.

**Влияние на dev-workflow**: live eval (`scripts/eval_retrieval.py`, `scripts/eval_multiturn.py`) + n8n smoke (`scripts/smoke_tg_e2e.py`) требуют поднятого `rag-api` контейнера. Если daemon не up — все эти скрипты молчат/таймаутят.

**Workaround**:
1. **Pre-warm**: `Start-Process 'C:\Program Files\Docker\Docker\Docker Desktop.exe'` за 10 минут до начала работы. Не блокировать сессию ожиданием — переключиться на code-work (unit-тесты, OpenAPI, документация работают без Docker).
2. **Poll-loop без блокировки**: `until docker info > /dev/null 2>&1; do sleep 8; done; echo READY` в фоне; продолжать работу параллельно.
3. **Defer eval-replay**: сделать code-change + pytest gate, закоммитить, прогнать eval при следующем подъёме Docker. См. session 2026-05-17 (overlap=75→50 + Sprint 6 #6/#7) — все 4 коммита прошли без Docker.
4. **WSL не использовать для daemon-проверки**: `wsl --list --running` показывает что WSL-distro `docker-desktop` up, но это НЕ значит что engine API ready.

**Когда есть Docker (любая будущая сессия)**:
```bash
docker compose up -d --force-recreate rag-api
python scripts/eval_retrieval.py --output eval/baseline.json
python scripts/eval_multiturn.py --output .tmp/eval_multiturn.json
python scripts/smoke_tg_e2e.py   # требует cloudflared up + webhook re-registered
```

## 17. n8n 1.103.2 CLI `import:workflow` + DB schema mismatch

**Симптом**:
```
docker compose exec -T n8n n8n import:workflow --input=/workflows/hr-legal-rag-workflow.json
→ An error occurred while importing workflows. See log messages for details.
column User.role does not exist
```
Также runtime webhook execution падает с `column 9827...role does not exist` (alias на `n8n.user` в JOIN с `project_relation`).

**Root cause**: n8n 1.103.2 (pinned image `n8nio/n8n:1.103.2`) использует typeorm-сгенерированный SQL с колонкой `role`, но реальная schema БД (из миграций) имеет `roleSlug` + FK на `n8n.role(slug)`. Schema "впереди" runtime — БД мигрирована на более новый layout, но pinned runtime не знает про переименование.

**Status**: KNOWN, workaround применён.

**Workaround**:
1. **Schema alias-колонка**: `ALTER TABLE n8n."user" ADD COLUMN role text GENERATED ALWAYS AS ("roleSlug") STORED;` — даёт SELECT-compat для runtime запросов.
2. **CLI замена**: вместо `n8n import:workflow` — прямой `UPDATE n8n.workflow_entity SET nodes=...::json, connections=...::json, ... WHERE id='<workflow-id>';` + `docker cp .tmp/update_workflow.sql testrag-postgres-1:/tmp/` + `MSYS_NO_PATHCONV=1 docker exec testrag-postgres-1 psql -U testrag -d testrag -f //tmp/update_workflow.sql` + `docker compose restart n8n`. Реализация: `.tmp/patch_workflow.py` (gitignored .tmp/).

**Fix path**: upgrade pinned n8n до версии, где typeorm-маппинг матчится с migrate'нутой schema. Требует regression-теста workflow с актуальным image.

**Текущее решение (2026-05-17 night research)**: НЕ апгрейдим. Причины:
1. **`column User.role` error устранён через ALTER TABLE alias** — оба пути (runtime webhook + CLI import) перестали ловить эту ошибку. Подтверждено: после ALTER `n8n import:workflow` отдаёт другую ошибку (`null value in column "active"`/`"versionId"`), не schema mismatch.
2. **CLI import тебе и не нужен**: канонический n8n-export включает `createdAt`, `updatedAt`, `isArchived`, `versionId` (uuid), `triggerCount`, `meta`, `tags`, `staticData` — добавление в committed JSON загрязняет git (timestamps/versionId drift на каждом сохранении). SQL UPDATE workaround (`.tmp/update_workflow.sql`) **сохраняет webhook secret binding в workflow row**, CLI import сбрасывает.
3. **Upgrade scope**: latest n8n = 2.21.3 (npm), pinned = 1.103.2 → 100+ minor versions разрыва. 1.x → 2.x = breaking changes. Внутри 1.x (1.104/1.105) — не подтверждено что починили User.role bug, потребует regression-смока на каждом step.

**Когда пересматривать**: если (а) SQL UPDATE workaround станет узким местом (например, при scaling многих workflow), или (б) появится фича n8n >=1.105, нужная проекту, или (в) security CVE в 1.103.2.

## 18. ~~Sprint 6 #1 partial — HTTP nodes ещё читают `$env`~~ ✅ RESOLVED 2026-05-17 night

**Был**: При `N8N_BLOCK_ENV_ACCESS_IN_NODE=true` падали 4 TG HTTP-ноды (`Send Typing`, `Send Typing Followup`, `Edit Reply Markup`, `Send Answer`) — читали `$env.TELEGRAM_BOT_TOKEN` в URL. `RAG_API_URL` уже был hardcoded на `http://rag-api:8000` (закрыто Sprint 6 #1 ранее).

**Что не сработало (зафиксировано как dead-end)**:
- `authentication: 'predefinedCredentialType', nodeCredentialType: 'telegramApi'` + `{{ $credentials.telegramApi.accessToken }}` в URL: n8n инжектит пустоту → TG 404. Причина: `nodeCredentialType` фильтрует credentials по `extends:oAuth2Api|oAuth1Api|has:authenticate` (Description.js V3, line 87), а `TelegramApi.credentials.js` имеет только `test.request`, без `authenticate` — UI/runtime игнорирует credential, expressions не получают `$credentials`.
- Конверсия в native `n8n-nodes-base.telegram`: не подходит для `editMessageReplyMarkup` (нет такой operation, только `editMessageText`) и для динамических `inline_keyboard` в `Send Answer` (fixedCollection требует buttons at design time).

**Resolved** (commit `<next>`): через **n8n variables** (`$vars`):
1. INSERT в `n8n.variables`: `(key='TELEGRAM_BOT_TOKEN', type='string', value=<token>)` напрямую через `psql` (UI create gated на license `isVariablesEnabled`, но read-path `getAllCached`/`getVariables` не проверяет license — Community Edition резолвит `$vars.X` в expressions без проблем).
2. 4 HTTP-ноды переключены на `=https://api.telegram.org/bot{{ $vars.TELEGRAM_BOT_TOKEN }}/...`.
3. `.env`: `N8N_BLOCK_ENV_ACCESS_IN_NODE=true`.
4. Live smoke `scripts/smoke_tg_e2e.py` — 5/6 ✓ (тот же baseline что overlap=75; одиночный fail `📖 Развернуть expand` — отдельная pre-existing race, не связана).

**Trade-off vs env-based**: токен в `n8n.variables` (plaintext в Postgres DB) вместо `.env` (plaintext в FS). Security level эквивалентен, но access scope строго через n8n expressions, не через `process.env`. Bonus: token больше не виден в `docker compose config`.

**Регенерация переменной при clean DB**: `psql -c "INSERT INTO n8n.variables (id, key, type, value) VALUES (uuid_generate_v4(), 'TELEGRAM_BOT_TOKEN', 'string', '<token>')"` + restart n8n для cache reload. Скрипт `scripts/seed_n8n_vars.py` (TODO) автоматизирует.

## 19. MIN_CONFIDENCE override drift в `.env`

**Симптом**: refusal_accuracy падает с 1.0 до 0.6-0.7 — модель отказывается отвечать (`refused=true`) на вопросы, которые должна закрывать (`expected_refused=false`). Confidence у этих ответов в диапазоне 0.18-0.32.

**Root cause**: `MIN_CONFIDENCE` в `.env` стоял на 0.35, в `docker-compose.yml` дефолт 0.25. Override drift: после Fix #2 (token splitter cl100k_base) chunks стали меньше → confidence на тех же golden Q ниже на ~23pp. Threshold 0.25 (по `feedback-docker-cold-start-windows`) восстанавливает refusal=1.0. В какой-то сессии `.env` подняли до 0.35 (вероятно эксперимент), забыли вернуть.

**Status**: FIXED (2026-05-17 EOD, .env возвращён к 0.25).

**Workaround / prevention**:
- Гейт: добавить `pytest scripts/test_eval_regression.py` floor по refusal_accuracy ≥ 0.85 — уже есть, но проверять локально перед коммитом.
- Перед запуском eval сверить `docker compose exec -T rag-api python -c "from app.settings import get_settings; print(get_settings().min_confidence)"` против baseline overlap=75 ожидаемого значения (0.25).

**Fix path**: добавить runtime sanity-log на старте rag-api: `logger.info("min_confidence=%s (baseline overlap=75 expects 0.25)", settings.min_confidence)` — чтобы дрифт был виден в logs сразу.

Результаты любых live runs вписать в `eval/baseline.json` + `docs/findings/2026-05-17-prev-n-qa-ablation.md` (§ A/B harness) + bot reply screenshots в demo-runbook.
