# Opus Result Followup: Greeting Route Static Triage

> Status 2026-05-16: Codex implemented the direct-reply route after this pre-fix triage was written. Keep this file as incident history and evidence checklist; the current workflow no longer sends `привет` through `/ask`.

> Источник: `n8n/workflows/hr-legal-rag-workflow.json` (read-only), `rag-api/app/main.py` lines 547–615 (read-only).
> Сценарий: пользователь шлёт `привет` в Telegram — ответа нет.
> Назначение: показать, на каком узле и почему молчание возможно, без live-проверок.
> Никакие файлы не редактировались.

## Topology (из checked-in JSON)

```
TelegramTrigger
   │  message | callback_query
   ▼
Whitelist (code)
   │  json: { authorized, event_type, chat_id, user_id, text, rating, request_log_id }
   ▼
Authorized?  ── false ─►  Send Denied (telegram)
   │ true
   ▼
Feedback?    ── true ──►  Send Feedback (HTTP /feedback) ──► Format Feedback ──► Send Feedback Ack
   │ false (question)
   ▼
Ask RAG API (HTTP POST {RAG_API_URL}/ask, body={question:text, telegram_user_id, top_k:5})
   ▼
Format Answer (code: text from answer + confidence + sources)
   ▼
Send Answer (telegram, with inlineKeyboard Good/Bad)
```

## Expected behavior per entry-point (static prediction)

### 1) `привет`

- TelegramTrigger получает `message.text = "привет"`.
- Whitelist:
  - `callbackData = ''`, `feedbackParts = []`, `isFeedback = false` → `event_type = 'question'`.
  - `text = "привет"`, `chat_id = message.chat.id`, `user_id` = строка.
  - Если `allowed.length === 0` → `authorized=false` с просьбой добавить ID.
  - Если user в whitelist → `authorized=true, event_type='question'`.
- Authorized? → true → Feedback? → false → Ask RAG API.
- `/ask` body: `{"question":"привет","telegram_user_id":"<id>","top_k":5}` — pydantic `min_length=1` пройдён.
- RAG API:
  - retriever ищет по «привет» — низкий confidence, мало sources.
  - `runtime.policy.can_answer(...)` скорее всего вернёт false → `refused=true`, `answer="Не хватает надежных источников для ответа. Уточните вопрос или добавьте документ в базу знаний."`
  - Если Mistral включён и `can_answer=true`: `mistral_answer = await runtime.llm.answer("привет", results)`. Mistral на голое «привет» без context может вернуть что-то вроде «Здравствуйте! Чем могу помочь?» — но потом срабатывает проверка `mistral_answer.strip().lower().startswith(("данных недостаточно", "не хватает", "не нашел", "не нашёл"))` — для приветствия НЕ срабатывает, ответ уходит. Не молчание.
- Format Answer: `text = answer + "\n\nConfidence: " + confidence + "\nИсточники:\n..."` или просто `answer + "\n\nConfidence: " + confidence + "\n"`.
- Send Answer: Telegram sendMessage с inlineKeyboard Good/Bad.

**Ожидаемый результат:** **должен прийти текст** (refusal с confidence или эхо приветствия).

### 2) `/start`

- TelegramTrigger ловит как обычное `message.text = "/start"`.
- Whitelist обрабатывает как `event_type='question'` (нет special-case для commands).
- /ask body: `{"question":"/start", top_k:5}` — `min_length=1` ок.
- RAG API: retriever, естественно, не нашёл совпадений → refusal.
- Ответ приходит = refusal text + confidence.

**Ожидаемый результат:** refusal text. **Greeting/help отсутствует как отдельный node — это UX gap, не silence.**

### 3) Тематический вопрос («сколько длится испытательный срок ...»)

- То же, что (1), но retriever находит chunks из `01_hr_probation_procedure.md` → confidence высокий → `refused=false`.
- Send Answer отправляет ответ Mistral + sources + inline keyboard.

**Ожидаемый результат:** полноценный ответ.

### 4) Неавторизованный пользователь

- Whitelist: `userId` не в `allowed` → `authorized=false`, `text="Доступ запрещен. Ваш Telegram ID: <id>."`.
- Authorized? → false → Send Denied → Telegram отправляет отказ.

**Ожидаемый результат:** «Доступ запрещен. Ваш Telegram ID: ...».

### 5) Feedback callback (кнопка Good/Bad)

- TelegramTrigger ловит `callback_query.data = "feedback:good:<request_log_id>"`.
- Whitelist:
  - `callbackData = "feedback:good:<id>"`, `feedbackParts = ['feedback','good',<id>]`, `isFeedback = true`.
  - `event_type = 'feedback'`, `rating='good'`, `request_log_id=<id>`.
- Authorized? → true → Feedback? → true → Send Feedback (POST /feedback).
- /feedback валидирует `rating in {good, bad}` (см. main.py:601) — ок.
- Возвращает `{"status": "accepted"}`.
- Format Feedback: `text="Оценка принята."`, `chat_id` тянется из `$node['Whitelist'].json.chat_id`.
- Send Feedback Ack: отправляет «Оценка принята.».

**Ожидаемый результат:** «Оценка принята.»

---

## Likely silence points (ранжировано)

### S1. Telegram node inlineKeyboard format может быть неверным [HIGH]

```json
"additionalFields": {
  "replyMarkup": "inlineKeyboard",
  "inlineKeyboard": {
    "rows": [
      { "row": { "buttons": [...] } }
    ]
  }
}
```

Структура `rows[i].row.buttons` — нестандартная для n8n-nodes-base Telegram node. В версии 1.2 формат обычно `inlineKeyboard.rows: [{ buttons: [...] }]` (без обёртки `row`). При невалидной структуре node либо:

- посылает reply_markup, который Telegram API отклоняет → ошибка → нет сообщения у пользователя;
- node на этапе валидации откладывает выполнение в error branch (если есть Continue On Fail) либо падает.

**Why это похоже на silence:** для пользователя нет ответа, в n8n executions виден failed run.

**Codex evidence to collect (live):**
- Открыть последний execution «Send Answer» → JSON output / error.
- Если ошибка вида `Bad Request: can't parse reply_markup` → подтверждено.

### S2. `$node['Whitelist'].json.chat_id` undefined в Format Answer / Format Feedback [HIGH]

Format Answer code:
```js
return [{ json: { chat_id: $node['Whitelist'].json.chat_id, text, request_log_id: ... } }];
```

`$node['Whitelist']` — legacy в n8n v1.x. Рекомендуемый синтаксис — `$('Whitelist').first().json` или `$items('Whitelist',0,0).json`. Если в текущей версии n8n legacy form возвращает `undefined`, `chat_id` будет `undefined`, и Send Answer вызовет sendMessage без chat_id → Telegram error 400.

**Codex evidence:**
- В execution view «Format Answer» → output JSON: посмотреть, есть ли `chat_id: <число>` или `chat_id: null`.

### S3. Mistral таймаут на коротких запросах («привет») [MEDIUM]

`runtime.llm.answer(request.question, results)` — async. Если Mistral отвечает медленно или ретраит на коротком payload, общий /ask может занять > timeout HTTP node n8n (по умолчанию 300s, но если переопределён ниже — критично).

**Codex evidence:**
- Execution view «Ask RAG API» → duration / error.
- `rag-api/` логи: `docker compose logs rag-api --tail=200 --since 10m`.
- Если node errored с `ECONNRESET` или `Request timed out` → подтверждено.

### S4. RAG /ask вернул пустой `answer` [MEDIUM]

Сценарий, в котором `mistral_answer = ""` и `build_grounded_answer(...) = ""`:
- Pydantic `AskResponse.answer: str` пустую строку ПРОПУСТИТ (нет min_length).
- Format Answer `text = "" + "\n\nConfidence: " + ...` — текст не пустой, Telegram примет.

**Real risk:** только если `build_grounded_answer` возвращает empty AND Mistral возвращает None. По коду `main.py:573` — `answer = mistral_answer or build_grounded_answer(...)`. Refusal path всегда возвращает фиксированный текст. Этот сценарий маловероятен, но возможен при отключённом Mistral + пустом retrieval.

**Codex evidence:** в request_logs SQL — `select answer from request_logs where question='привет' order by id desc limit 1;`

### S5. Telegram webhook указывает на устаревший tunnel URL [MEDIUM]

R1 из `opus_result_followup_risk_burndown.md`. trycloudflare URL умер при рестарте, BotFather всё ещё держит старый webhook. Telegram отправляет update → 404/timeout → n8n даже не получает event.

**Codex evidence:**
- В Telegram bot API: `getWebhookInfo` → `url`, `last_error_date`, `last_error_message`. **Не печатать в чат токен** — выполнить локально и зачитать только поля.
- n8n executions list: если **нет** execution за время теста — событие не дошло.

### S6. Workflow active=false [LOW]

`mvp-plan.md §Current Status` пишет, что workflow активирован. Если Codex перезапустил n8n и забыл re-activate — workflow слушает webhook, но trigger не сохраняет executions.

**Codex evidence:**
- `select active from n8n.workflow_entity where id='testrag-hr-legal-assistant';` → должен быть `t`.

### S7. Telegram credential `testrag-telegram-api` отсутствует / неверный токен [LOW]

Workflow ссылается на credential `id="testrag-telegram-api"`. Если этот credential в n8n DB не привязан, либо токен в нём устарел, sendMessage упадёт.

**Codex evidence:**
- В n8n UI → Credentials → проверить наличие `TestRag Telegram Bot` с id `testrag-telegram-api`. **Токен не показывать.**

### S8. TelegramTrigger updates filter [LOW]

`updates: ["message", "callback_query"]` — корректно. Если бы было только `callback_query`, плейн text сообщения проходили бы мимо. На данный момент — ОК.

### S9. RAG_API_URL env var не установлен в контейнере n8n [LOW]

В Ask RAG API node: `url: ={{ $env.RAG_API_URL }}/ask`. Если env пуст или указывает на localhost (а не на сервис `rag-api`), HTTP fails.

**Codex evidence:**
- `docker compose exec -T n8n printenv RAG_API_URL` (значение типа `http://rag-api:8000` — не secret).

### S10. n8n Code node v2 не поддерживает `$node` syntax в коде [LOW-MEDIUM]

В n8n v1.x Code node typeVersion 2 использует context object. Legacy `$node['Name']` через Code должно работать через JavaScript Code (`mode: runOnceForEachItem` или `runOnceForAllItems` — не указано в JSON, значит default). Если default — runOnceForAllItems — `$node` корректен. Если изменилось — undefined.

**Codex evidence:** Format Answer → tab `Settings` → `Mode`. Если `Run Once for Each Item` и используется `$node['Whitelist']` без `.first()` — поведение зависит от версии n8n.

---

## UX gaps в greeting route (не silence, но плохо)

| Gap | Где | Эффект |
|---|---|---|
| Нет special-case для `/start` | Whitelist | `/start` → /ask → refusal вместо приветствия |
| Нет special-case для коротких приветствий (`привет`, `hi`, `здравствуйте`) | Whitelist | то же |
| Нет thanks-обработки («спасибо») | Whitelist | те же refusal'ы |
| Format Answer не отделяет `refused=true` от `refused=false` | Format Answer | refusal-сообщение всё равно показывает `Confidence: 0.0` (странно для пользователя) |
| Inline keyboard Good/Bad шлётся даже при refused | Send Answer | пользователь может оценить пустой ответ |

Эти gap'ы не объясняют silence сами по себе, но Codex стоит закрыть в том же patch'е.

---

## Evidence checklist для Codex (live)

| # | Что собрать | Команда / источник | Что подтверждает |
|---|-------------|---------------------|------------------|
| E1 | Дошёл ли event до n8n | n8n UI → Executions, фильтр по timestamp теста | если 0 executions → webhook (S5) или workflow inactive (S6) |
| E2 | Output Whitelist | execution → Whitelist node JSON | `chat_id`, `text`, `event_type`, `authorized` |
| E3 | Output Ask RAG API | execution → Ask RAG API JSON | `answer`, `confidence`, `refused`, HTTP status |
| E4 | Output Format Answer | execution → Format Answer JSON | `text` непустой и `chat_id` число |
| E5 | Output Send Answer | execution → Send Answer JSON / error | если error: текст ошибки от Telegram API |
| E6 | RAG API логи | `docker compose logs rag-api --since 10m` | trace на /ask, exceptions, latency |
| E7 | Webhook info | `curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo` (off-screen!) | `last_error_message`, `url`, `pending_update_count` |
| E8 | Workflow active | psql `select active from n8n.workflow_entity where id='testrag-hr-legal-assistant';` | `t` |
| E9 | RAG_API_URL в n8n | `docker compose exec -T n8n printenv RAG_API_URL` | соответствует `http://rag-api:8000` |
| E10 | request_logs последняя запись | `select id,question,refused,answer from request_logs order by id desc limit 1;` | подтверждает, что /ask вообще вызывался |

**Off-screen (E7):** обязательно вне share-экрана — содержит TOKEN в URL.

---

## Decision tree для Codex (порядок проверки)

```
E1 (есть execution за окно теста?)
 ├─ нет → E7 (webhook валиден?)
 │         ├─ last_error_message заполнено → S5 (stale tunnel) → пересоздать tunnel + setWebhook
 │         └─ нет error → E8 (workflow active?)
 │                        ├─ f → activate workflow
 │                        └─ t → событие потеряно где-то ниже (рег.интерфейс TG)
 ├─ есть → E2 (Whitelist output OK?)
 │         ├─ chat_id null → проверить, доставил ли TelegramTrigger полный объект message
 │         ├─ authorized=false → S5/S7 unrelated; user не в whitelist
 │         └─ authorized=true, event_type='question'
 │             └─ E3 (Ask RAG API output)
 │                  ├─ HTTP error → E9 (RAG_API_URL) + E6 (rag-api logs)
 │                  ├─ HTTP 200, refused=true, answer непустой → norm. ожидаемый refusal
 │                  ├─ HTTP 200, answer пустой → S4
 │                  └─ HTTP 200, answer ок → E4 (Format Answer)
 │                      ├─ text пустой / chat_id null → S2 (legacy $node)
 │                      └─ норм → E5 (Send Answer)
 │                          ├─ error «can't parse reply_markup» → S1 (inline keyboard format)
 │                          ├─ error «chat not found» → chat_id потерян по дороге
 │                          ├─ success → проблема ВНЕ n8n (Telegram doesn't deliver to user)
 │                          └─ telegram credential error → S7
 │
```

---

## Что **офлайн** уже видно

| Наблюдение | Источник | Что означает |
|---|---|---|
| `Whitelist` ставит `event_type='question'` на любой текст, включая `/start` и `привет` | n8n JSON line 30 | UX gap: нет greeting branch |
| `$node['Whitelist'].json.chat_id` используется в двух Code nodes | n8n JSON lines 119, 132 | при определённых конфигурациях n8n v1 — fragile |
| inline keyboard вложен в `rows[i].row.buttons` | n8n JSON lines 149–169 | подозрение на неверный формат для node typeVersion 1.2 |
| /ask всегда возвращает непустой `answer` | rag-api/app/main.py:569–579 | пустой answer не объясняет silence |
| /ask refusal text — фиксированный | rag-api/app/main.py:570 | пользователь должен видеть его, если doalo |

---

## Что НЕ покрыто этим триаджем

- Содержимое `runtime.llm.answer`, `build_grounded_answer`, `confidence_from_results` — не открывал детальнее, чтобы не редактировать рекурсивно.
- Настройки HTTP timeout у `Ask RAG API` node — в JSON `options: {}`, значит default n8n.
- Реальная версия n8n в контейнере — Codex смотрит в `docker compose exec n8n n8n --version`.

## Verification (self-check)

- 5 entry-points (`привет`, `/start`, тематический вопрос, unauth, feedback) разобраны от Trigger до Send.
- 10 silence-points ранжированы с приоритетом и evidence для каждого.
- Decision tree связывает 10 точек evidence с конкретными root cause.
- UX gaps выделены отдельно от silence — Codex может закрыть в том же patch.
- Live-команды помечены: E7 — off-screen (содержит TOKEN).
- Проектные файлы не редактировались.
