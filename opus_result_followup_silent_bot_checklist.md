# Opus Result Followup: Silent-Bot Failure-Mode Checklist

> Status 2026-05-16: Codex fixed the observed greeting silence and verified the live direct-reply path. Keep this checklist for future Telegram/n8n incidents.

> Сценарий: пользователь отправил сообщение в Telegram — ответа нет. Причина может быть на любой из 6 границ.
> Назначение: для каждой границы — симптом, offline-проверка (что может сделать Opus), live-проверка (что только Codex).
> Источник: `n8n/workflows/hr-legal-rag-workflow.json`, `rag-api/app/main.py`, `opus_result_followup_greeting_route_triage.md`.
> Никакие файлы не редактировались.

## Граничный flow

```
[1] Telegram client                — пользователь отправляет
       │ HTTPS POST к Telegram cloud
       ▼
[2] Telegram cloud                 — внутри их инфры
       │ HTTPS POST на webhook (cloudflared tunnel)
       ▼
[3] cloudflared tunnel             — Docker container testrag-cloudflared
       │ HTTP → http://n8n:5678/webhook/...
       ▼
[4] n8n webhook / TelegramTrigger  — получает event
       │
       ▼
[5] Whitelist → Authorized? → Feedback?  — внутренняя логика
       │
       ▼
[6] Ask RAG API (HTTP)             — POST → http://rag-api:8000/ask
       │
       ▼
[7] Format Answer (code)           — строит text + chat_id
       │
       ▼
[8] Send Answer (Telegram node)    — sendMessage с inline keyboard
       │
       ▼
[9] Telegram cloud → user
```

Границы 1, 2, 9 — за пределами проекта. Триаж концентрируется на 3–8.

---

## B1. Telegram cloud → cloudflared tunnel

### Симптомы

- В n8n executions **нет** записей за время теста.
- Telegram `getWebhookInfo` показывает `last_error_message` (DNS error, timeout, 5xx).
- `pending_update_count` > 0 и растёт.

### Offline-проверки (Opus может)

| # | Проверка | Где смотреть | Что подтверждает |
|---|----------|-------------|-------------------|
| B1.O1 | Структура webhook конфигурации | `docs/demo-runbook.md` §Локальный Telegram Webhook lines 63–90 | команды и переменные оформлены верно; tunnel запускается отдельным `docker run`, не из compose |
| B1.O2 | Tunnel НЕ в docker-compose | `docker-compose.yml` (не открываю по hard rule) | если cloudflared отсутствует в compose, ребут Docker Desktop ≡ потеря tunnel |
| B1.O3 | `.env` шаблон | `.env.example` (не открываю) | проверить, что `N8N_WEBHOOK_URL` указан как переменная |

### Live-проверки (только Codex)

| # | Команда | Pass signal |
|---|---------|-------------|
| B1.L1 | `docker ps --filter "name=testrag-cloudflared"` | контейнер `Up`, не `Exited` |
| B1.L2 | `docker logs testrag-cloudflared --tail 50` (**off-screen** — содержит URL!) | нет повторных «registered connection 0...4», нет «context deadline exceeded» |
| B1.L3 | `getWebhookInfo` (off-screen) | `url` совпадает с `N8N_WEBHOOK_URL`, `last_error_message` пуст, `last_error_date` старее теста |
| B1.L4 | `Invoke-WebRequest -Uri (...N8N_WEBHOOK_URL...); .StatusCode` | 200/401/404 (любое значимое), не timeout |

### Если граница виновна

→ R1 (stale tunnel). Mitigation: пересоздать tunnel, обновить `.env`, `docker compose up -d --force-recreate n8n`, BotFather `setWebhook`.

---

## B2. cloudflared tunnel → n8n container

### Симптомы

- cloudflared жив (B1 OK), но n8n executions пусты.
- `n8n` контейнер в `unhealthy` / `restarting`.

### Offline-проверки

| # | Проверка | Где смотреть | Что подтверждает |
|---|----------|-------------|-------------------|
| B2.O1 | docker network в demo-runbook | `docs/demo-runbook.md` line 85: `--network testrag_default` | если у пользователя `compose v2` нормализует имя как `testrag-default`, cloudflared не подключится |
| B2.O2 | n8n port mapping | `docker-compose.yml` (read-only allowed) | n8n должен слушать `:5678` внутри сети |

### Live-проверки (только Codex)

| # | Команда | Pass signal |
|---|---------|-------------|
| B2.L1 | `docker network ls --filter name=testrag` | существует одна сеть; имя совпадает с тем, что использует cloudflared |
| B2.L2 | `docker network inspect <name>` | в сети присутствуют `testrag-n8n`, `testrag-cloudflared` |
| B2.L3 | `docker compose exec -T cloudflared wget -qO- http://n8n:5678/healthz` | 200 (если внутри tunnel-контейнера резолвится) |
| B2.L4 | `Invoke-WebRequest http://localhost:5678/healthz; .StatusCode` | 200 (с host машины) |

### Если граница виновна

→ network mismatch (finding #6 из docs_consistency). Mitigation: подключить cloudflared к актуальной сети.

---

## B3. n8n TelegramTrigger node

### Симптомы

- Webhook доставляет event (B1, B2 OK), но executions нет ИЛИ есть с `error` на TelegramTrigger.
- Workflow status `inactive`.

### Offline-проверки

| # | Проверка | Где смотреть | Что подтверждает |
|---|----------|-------------|-------------------|
| B3.O1 | `updates` filter | `n8n/workflows/hr-legal-rag-workflow.json:7–10` | значения `["message","callback_query"]` — message пройдёт |
| B3.O2 | typeVersion TelegramTrigger | line 16: `"typeVersion": 1.3` | если установленный n8n не имеет node version 1.3 (более старая ставка), trigger не сериализуется |
| B3.O3 | Credential id | line 23: `"id": "testrag-telegram-api"` | в n8n DB должна быть credential с этим ID |

### Live-проверки

| # | Команда | Pass signal |
|---|---------|-------------|
| B3.L1 | SQL `select active from n8n.workflow_entity where id='testrag-hr-legal-assistant';` | `t` |
| B3.L2 | n8n UI → Credentials → `TestRag Telegram Bot` (id `testrag-telegram-api`) | существует, не показывать токен |
| B3.L3 | `docker compose exec n8n n8n --version` | поддерживает typeVersion 1.3 (n8n 1.x) |
| B3.L4 | n8n UI → Executions → последние 10 минут | в каждой execution есть `TelegramTrigger` node со статусом success |

### Если граница виновна

→ workflow inactive, credential mismatch, или version mismatch. Mitigation: `n8n update:workflow --active=true`, проверить credential, обновить n8n image.

---

## B4. Whitelist & routing nodes (Whitelist, Authorized?, Feedback?)

### Симптомы

- TelegramTrigger получил event, но дальше workflow обрывается.
- В execution view виден empty output на одном из узлов.
- Конкретно для greeting silence: путь проходит, но `chat_id`/`text` теряются.

### Offline-проверки

| # | Проверка | Где смотреть | Что подтверждает |
|---|----------|-------------|-------------------|
| B4.O1 | Whitelist parsing `from.id` | n8n JSON line 30 | `userId = String(from.id || '')` — пустой userId не блокирует возврат `authorized=false` с сообщением «Whitelist не настроен» (если `allowed.length === 0`) |
| B4.O2 | event_type detection | line 30 | feedback только по callback с префиксом `feedback:`; все остальные сообщения → `'question'` |
| B4.O3 | `text` extraction | line 30: `text: message.text \|\| callbackData \|\| ''` | пустой text возможен, /ask может вернуть 422 |

### Live-проверки

| # | Команда | Pass signal |
|---|---------|-------------|
| B4.L1 | execution → Whitelist node output JSON | `authorized: true`, `event_type: 'question'`, `chat_id: <number>`, `text: 'привет'`, `user_id: '<id>'` |
| B4.L2 | execution → Authorized? IF output | true-branch активен |
| B4.L3 | execution → Feedback? IF output | false-branch (question) активен |

### Если граница виновна

→ user_id не в `ALLOWED_TELEGRAM_USER_IDS`, callback_query доставлен как message, или text пустой. Mitigation: обновить `.env`, перезапустить n8n. Для greeting → добавить routing из `opus_result_followup_greeting_contract.md`.

---

## B5. Ask RAG API HTTP node

### Симптомы

- Whitelist прошёл с question, но `Format Answer` не вызвался.
- В execution view узел `Ask RAG API` со статусом `error`.

### Offline-проверки

| # | Проверка | Где смотреть | Что подтверждает |
|---|----------|-------------|-------------------|
| B5.O1 | URL шаблон | n8n JSON line 84: `={{ $env.RAG_API_URL }}/ask` | требует env переменную |
| B5.O2 | Body shape | line 87: `JSON.stringify({ question: $json.text, telegram_user_id: $json.user_id, top_k: 5 })` | совпадает с `AskRequest` pydantic (`rag-api/app/main.py:38–41`) |
| B5.O3 | top_k=5 в пределах [1,10] | pydantic `ge=1, le=10` | ок |
| B5.O4 | Никакого timeout override в node options | line 88: `options: {}` | default timeout n8n (5 мин в v1.x) |

### Live-проверки

| # | Команда | Pass signal |
|---|---------|-------------|
| B5.L1 | execution → Ask RAG API output | HTTP status 200, body содержит `answer`, `confidence`, `refused`, `sources` |
| B5.L2 | `docker compose exec n8n printenv RAG_API_URL` | значение типа `http://rag-api:8000` |
| B5.L3 | rag-api logs `docker compose logs rag-api --since 10m` | для теста виден INFO-лог `POST /ask 200`, latency < таймаут |
| B5.L4 | psql `select id,question,answer,refused from request_logs order by id desc limit 3;` | последняя запись соответствует тесту |

### Если граница виновна

→ RAG_API_URL не выставлен, Mistral медленный, retriever упал. Mitigation: проверить env, логи rag-api, отключить Mistral (extractive only) на демо.

---

## B6. Format Answer code node

### Симптомы

- `Ask RAG API` вернул 200, но `Send Answer` не отправил сообщение.
- В execution view `Format Answer` либо empty output, либо текст странный (`undefined\n\nConfidence: undefined\n`).

### Offline-проверки

| # | Проверка | Где смотреть | Что подтверждает |
|---|----------|-------------|-------------------|
| B6.O1 | `$node['Whitelist'].json.chat_id` legacy | n8n JSON line 119 | в современной n8n рекомендован `$('Whitelist').first().json`. Legacy form fragile |
| B6.O2 | text template | line 119: `${$json.answer}\n\nConfidence: ${$json.confidence}\n${sources ? ...}` | если `answer` пустой строкой, text = «\n\nConfidence: 0.0\n» — не пустой, но cryptic |
| B6.O3 | `request_log_id` пробрасывается | line 119: `request_log_id: $json.request_log_id \|\| ''` | inline кнопки получат пустой `request_log_id`, что нормально для refusal |

### Live-проверки

| # | Команда | Pass signal |
|---|---------|-------------|
| B6.L1 | execution → Format Answer output | `chat_id: <number>`, `text: <непустой>`, `request_log_id: <string>` |
| B6.L2 | если text начинается с `undefined` | Mistral / pydantic вернул нечто, не соответствующее `AskResponse` |
| B6.L3 | если chat_id null | проблема legacy `$node` syntax — заменить на `$('Whitelist').first().json.chat_id` |

### Если граница виновна

→ legacy node access, или /ask вернул структуру без полей. Mitigation: обновить syntax, добавить defaults в Code node.

---

## B7. Send Answer Telegram node

### Симптомы

- `Format Answer` дал валидный output, но Telegram сообщение НЕ пришло.
- В execution view `Send Answer` со статусом `error`.

### Offline-проверки

| # | Проверка | Где смотреть | Что подтверждает |
|---|----------|-------------|-------------------|
| B7.O1 | Inline keyboard структура | n8n JSON lines 149–169 | нестандартная вложенность `rows[i].row.buttons` — подозрение |
| B7.O2 | reply_markup mode | line 148: `"replyMarkup": "inlineKeyboard"` | n8n требует строковое значение enum'а; ок |
| B7.O3 | chatId expression | line 145: `={{ $json.chat_id }}` | если chat_id `null` → Telegram API «chat not found» |
| B7.O4 | text expression | line 146: `={{ $json.text }}` | пустой text → Telegram «message text is empty» |

### Live-проверки

| # | Команда | Pass signal |
|---|---------|-------------|
| B7.L1 | execution → Send Answer output / error | если error содержит `Bad Request: can't parse reply_markup` → B7.O1 виновен |
| B7.L2 | error `Bad Request: message text is empty` | B6 → B7 связка с пустым text |
| B7.L3 | error `Bad Request: chat not found` | chat_id неверный |
| B7.L4 | error 401 / Forbidden | credential / token проблема |

### Если граница виновна

→ inline keyboard format ИЛИ chat_id ИЛИ text empty. Mitigation: исправить inline-keyboard на `rows: [{ buttons: [...] }]`, добавить fallback на пустой text/chat_id.

---

## B8. RAG API внутренняя логика

### Симптомы

- `/ask` доступен (B5 200), но `answer` пустой / некорректный / 500.

### Offline-проверки

| # | Проверка | Где смотреть | Что подтверждает |
|---|----------|-------------|-------------------|
| B8.O1 | refused path | `rag-api/app/main.py:569–570` | refusal text фиксированный, **не может быть пустым** |
| B8.O2 | mistral_answer + fallback | line 572–573 | `mistral_answer or build_grounded_answer(...)` — если оба пустые, answer = "" |
| B8.O3 | mistral_answer false-positive refusal | lines 574–578 | startswith({"данных недостаточно","не хватает","не нашел","не нашёл"}) → refused=true, confidence=0 |
| B8.O4 | request_log_id | line 580: `runtime.store.log_request(...)` | если postgres недоступен — возможен exception до return |

### Live-проверки

| # | Команда | Pass signal |
|---|---------|-------------|
| B8.L1 | `Invoke-RestMethod -Uri http://localhost:8000/ask -Method POST -ContentType 'application/json' -Body '{"question":"привет"}'` (UTF-8 byte-encoded!) | 200, `answer` непустой |
| B8.L2 | rag-api logs | exceptions, latency, Mistral 5xx |
| B8.L3 | psql `select postgres_enabled from ...` — нет такого; вместо: `/health` | `postgres_enabled=true` |

### Если граница виновна

→ Mistral возвращает пустую строку, build_grounded_answer не покрывает edge case «привет». Mitigation: добавить fallback в /ask или special-case на n8n уровне (см. greeting_contract).

---

## Сводная таблица «boundary → owner → command»

| Boundary | Symptom | Offline (Opus) | Live (Codex) |
|----------|---------|-----------------|---------------|
| B1 Telegram→tunnel | n8n executions пусты | docs/demo-runbook review | `getWebhookInfo`, `docker logs cloudflared` |
| B2 tunnel→n8n | executions пусты, cloudflared up | docker-compose review | `docker network inspect`, `wget` из контейнера |
| B3 TelegramTrigger | executions с error на Trigger | workflow JSON review | `n8n --version`, SQL `workflow_entity` |
| B4 Whitelist/IF | executions есть, обрывается на routing | JS code review | execution view JSON |
| B5 Ask RAG API | execution на /ask со status=error | URL/body review | rag-api logs, request_logs SQL |
| B6 Format Answer | output `chat_id=null` или text=`undefined` | legacy `$node` review | execution view JSON |
| B7 Send Answer | error «can't parse reply_markup» | inline keyboard review | execution view error |
| B8 RAG API logic | /ask 200 но answer пустой | main.py:559–596 review | curl /ask, rag-api logs |

## Priority of investigation для `привет` silence

Recommended Codex order (минимизирует время от reproduction до root cause):

1. **B7.L1** — execution view последнего failed run на Send Answer.
2. **B6.L1** — Format Answer output: chat_id и text заполнены?
3. **B5.L1** — Ask RAG API output: answer пустой?
4. **B3.L1, B3.L4** — workflow active + есть execution за окно теста.
5. **B1.L3** — webhook info (off-screen).

Этот порядок начинается с границы, ближайшей к user (B7), и идёт вверх. Большинство silence cases видны уже на шаге 1.

## Что Opus сделать НЕ может

- Запустить `getWebhookInfo` (содержит TOKEN в URL — нарушение hard rules).
- Запустить любые `docker compose exec` команды (hard rule «Do not run Docker commands»).
- Вызвать `/ask` (hard rule «Do not run ... external API commands»; локальный API формально тоже DB-mutating, лог пишет).
- Открыть n8n executions UI (это live действие).
- Прочитать `.env` или `.env.example` (hard rule).

Все эти проверки делегированы Codex; Opus подготовил для каждой точные команды и pass-signal.

## Verification (self-check)

- 8 границ покрыты (B1–B8), каждая разбита на симптомы, offline и live проверки.
- Никакие команды Opus не запускал.
- Recommended priority указан и обоснован.
- Чёткое разделение «Opus / Codex» по hard rules.
- Проектные файлы не редактировались.
