# Known Issues & Workarounds

Все известные проблемы TestRag MVP по состоянию на 2026-05-17 (HEAD `909bd42`). Каждая запись: симптом → root cause → текущий status → workaround/fix path.

## 1. Retrieval polluted после aviation pass

**Симптом**: `Что такое controlled zone?` даёт top-5 sources из `02_hr_tmp_*` (трудовой договор, удалёнка, приказ об отпуске) score 0.84-0.94. Ожидалось `01_hr_pol_safety.md` (раньше выдавал score 0.97).

**Root cause**: Aviation profile pass (commit `7c6951a`, 2026-05-16) переписал ВСЕ 200 corpus-файлов под авиагрузовую тематику, включая HR-шаблоны. Шаблоны трудового договора теперь содержат `controlled_zone_access`, `AWB`, `aviation security` ровно как safety policy. SQL подтверждение: `select d.file_name, count(*) from document_chunks c join documents d on c.document_id=d.id where c.content ilike '%controlled%zone%' group by 1 order by 2 desc` → 02_hr_tmp_employment_contract (5) > 02_hr_tmp_add_agreement (4) > 01_hr_pol_safety (1 реально релевантный).

**Status**: KNOWN, defer to Sprint 4.

**Workaround**: Mistral собирает корректный ответ из «не тех» source — пользователь видит правильное описание controlled zone, но «Источники:» снизу выглядят нерелевантно. Для демо-аудитории неочевидно.

**Fix candidates** (см. `docs/findings/2026-05-17-retrieval-aviation-pollution.md`):
- Re-profile aviation pass только tlog/safety/comp, HR-шаблоны вернуть к pre-aviation (3-5 часов работы)
- Boost section weight в HybridRetriever
- Cross-encoder reranker на top-20

## 2. TG webhook secret in-memory — синтетический POST невозможен

**Симптом**: `curl -X POST <N8N_WEBHOOK_URL>/webhook/...telegramtrigger/webhook -d '{...}'` → `403 {"message":"Provided secret is not valid"}`.

**Root cause**: n8n TelegramTrigger v1.3 генерит random secret_token при активации workflow, хранит in-memory (staticData=NULL в БД, webhook_entity.webhookId='' пустой). Передаёт в TG через `setWebhook(...secret_token=X)`. TG потом шлёт `X-Telegram-Bot-Api-Secret-Token: X` header — n8n валидирует.

**Status**: KNOWN, ограничивает автономное E2E тестирование.

**Workaround**:
1. Live TG smoke через @AIagentJu_bot (юзер вручную).
2. Bot API direct `sendMessage` — отправлять сформированный split-output в чат через Bot API без прохождения через webhook (см. `.tmp/smoke_split.py`).
3. pytest 68/68 покрывают workflow логику unit-level (Whitelist routing, Format Answer split, balance tags, parse_mode).

**Fix candidates** (без upstream-патча в n8n):
- Найти секрет в n8n process memory (грязный hack)
- Re-call TG `setWebhook(secret_token=KNOWN)` — но n8n всё равно валидирует против своего internal значения
- Patch TelegramTrigger node в форке n8n — overkill для MVP

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

## 10. Cloudflare tunnel — эфемерные URLs

**Симптом**: `docker compose down` + `docker compose up` → trycloudflare URL изменился → TG webhook указывает на dead URL → бот не отвечает.

**Status**: KNOWN. Процедура восстановления в `docs/demo-runbook.md` раздел «Локальный Telegram Webhook» (6 шагов: rm контейнера → новый run → grep URL → заменить `N8N_WEBHOOK_URL` в .env → recreate n8n → verify TG `getWebhookInfo`).

**Fix candidate**: купить cloudflare named tunnel ($0 для personal use, но требует регистрации домена) — стабильный URL. Или namesilo dns + custom tunnel. Out of MVP scope.

## 11. Workflow .ready vs editing races (CX-related)

Из global feedback memory: для CX-спеков. Не применимо к TestRag, но напомню — не редактировать `.workflow/inbox/*.md` после `touch .ready`. В TestRag CX не используется.

## 12. n8n editor требует логин (для UI отладки)

**Симптом**: `http://localhost:5678/rest/workflows` → 401. UI требует владельца аккаунта (setup wizard).

**Status**: KNOWN, не fix. Для отладки воркфлоу — через `docker compose exec n8n n8n ...` CLI и Postgres queries в `n8n.execution_entity` / `n8n.execution_data`.

## 13. Mistral 12-минутная задержка ответа (наблюдалась 1 раз)

**Симптом**: От «Что такое controlled zone?» (1:47 AM) до ответа (1:59 AM) прошло 12 минут.

**Root cause**: Подозрение на Mistral 429 retry с длинным backoff в `requests` или `httpx` client. Параллельно — n8n execution 17 показал реальный runtime 8.7 сек. Скорее всего: Cloudflare tunnel пересоздался, TG webhook задержался с доставкой, либо Mistral free tier забекдоффил.

**Status**: INTERMITTENT, не воспроизводится стабильно. Если повторится — добавить timing в логах rag-api.

## Сводка: что блокирует «production-ready»

| issue | блокирует demo? | блокирует prod? |
|---|---|---|
| 1 retrieval polluted | нет (Mistral компенсирует) | да |
| 2 webhook secret in-memory | нет (юзер тестит вручную) | нет |
| 3 MD→HTML | FIXED | FIXED |
| 4 $json shadowing | FIXED | FIXED |
| 5 4096 limit | FIXED | FIXED |
| 6 keyboard on split | FIXED | FIXED |
| 7 Mistral 429 | нет (graceful degrade) | да (paid tier needed) |
| 8 path mangling | нет | нет (CI Linux) |
| 9 rebuild requirement | нет | нет |
| 10 ephemeral tunnel | да (требует пересоздания при рестарте) | да (named tunnel или real domain) |
| 11 N/A | — | — |
| 12 n8n login | нет | нет (используем CLI/SQL) |
| 13 intermittent latency | нет | мониторить |

Демо-готовность: ⚠️ retrieval polluted source list (issue 1) + ephemeral tunnel (issue 10) — главные нерешённые. Sprint 4 (retrieval polish) — приоритет.
