# Demo Runbook

## Цель

Показать MVP-поток: вопрос в Telegram, обработка в n8n, запрос в RAG API, ответ с источниками и оценка ответа.

## Подготовка

1. Перевыпустить Telegram token в BotFather, если старый токен где-либо публиковался.
2. Скопировать `.env.example` в `.env`.
3. Заполнить `TELEGRAM_BOT_TOKEN`, `ALLOWED_TELEGRAM_USER_IDS`, при наличии `MISTRAL_API_KEY`.
4. Запустить Docker Desktop.
5. Запустить сервисы:

```powershell
docker compose up --build
```

6. Открыть n8n: `http://localhost:5678`.
7. Импортировать workflow `n8n/workflows/hr-legal-rag-workflow.json`.
8. Создать Telegram credentials в n8n UI.

## Корпус Документов

По умолчанию демо использует минимальный корпус `data/sample_docs`.

Для расширенного MVP-корпуса включить manifest mode в `.env`:

```env
DOCS_PATH=/app/corpus
DOCS_MANIFEST_PATH=/app/manifests/MVP_CORPUS_FILES.txt
```

После смены корпуса пересоздать `rag-api`:

```powershell
docker compose up -d --build --force-recreate rag-api
```

Manifest ограничивает индексацию выбранными файлами из `corpus/`, чтобы случайно не отправить все 200 документов на embeddings.

## Импорт n8n Через CLI

Если n8n уже запущен в Docker Compose, workflow и Telegram credential можно импортировать без UI.
Команды не должны печатать `TELEGRAM_BOT_TOKEN`.

```powershell
docker compose exec -T n8n n8n import:workflow --input=/workflows/hr-legal-rag-workflow.json --projectId=<project_id>
docker compose exec -T n8n n8n update:workflow --id=testrag-hr-legal-assistant --active=true
docker compose up -d --force-recreate n8n
```

`project_id` можно посмотреть в Postgres:

```powershell
@'
select id, name, type from n8n.project;
'@ | docker compose exec -T postgres psql -U testrag -d testrag
```

Credential `telegramApi` должен называться `TestRag Telegram Bot` и иметь id `testrag-telegram-api`.

После импорта проверить маршрутизацию IF-веток:

```powershell
@'
select
  connections->'Authorized?'->'main'->0->0->>'node' as authorized_true,
  connections->'Authorized?'->'main'->1->0->>'node' as authorized_false,
  connections->'Feedback?'->'main'->0->0->>'node' as feedback_true,
  connections->'Feedback?'->'main'->1->0->>'node' as feedback_false
from n8n.workflow_entity
where id='testrag-hr-legal-assistant';
'@ | docker compose exec -T postgres psql -U testrag -d testrag
```

Ожидаемо: `authorized_true=Feedback?`, `authorized_false=Send Denied`, `feedback_true=Send Feedback`, `feedback_false=Ask RAG API`.

Для актуальной версии workflow также должна быть direct-reply ветка для приветствий и служебных коротких сообщений:

```powershell
@'
select
  connections->'Feedback?'->'main'->1->0->>'node' as feedback_false,
  connections->'Direct Reply?'->'main'->0->0->>'node' as direct_reply_true,
  connections->'Direct Reply?'->'main'->1->0->>'node' as direct_reply_false
from n8n.workflow_entity
where id='testrag-hr-legal-assistant';
'@ | docker compose exec -T postgres psql -U testrag -d testrag
```

Ожидаемо: `feedback_false=Direct Reply?`, `direct_reply_true=Send Direct Reply`, `direct_reply_false=Ask RAG API`.

## Telegram polling-мост

Публичный HTTPS-туннель больше не нужен. Telegram-интерфейс работает через polling: `services/tg_poll_bridge/main.py` (Python, ~150 строк, stdlib-only) забирает обновления у Telegram API через `getUpdates` и POSTит их во внутренний webhook n8n.

Старт моста и проверка статуса:

```powershell
docker compose up -d tg_poll_bridge
docker logs testrag-tg_poll_bridge-1 --tail 20
```

Ожидаемо: в логах строки вида `polling offset=N updates=K`, без 4xx/5xx от Telegram API.

Проверить, что webhook у Telegram отключён (polling и webhook несовместимы):

```powershell
$token = ([regex]::Match((Get-Content .env -Raw), 'TELEGRAM_BOT_TOKEN=(\S+)')).Groups[1].Value
$info = Invoke-RestMethod -Uri "https://api.telegram.org/bot$token/getWebhookInfo"
"webhook url: '$($info.result.url)' (должно быть пустым при polling-режиме)"
"pending: $($info.result.pending_update_count)"
```

## Whitelist Telegram

Пустой `ALLOWED_TELEGRAM_USER_IDS` не открывает доступ всем. Бот ответит пользователю его Telegram ID и попросит добавить этот ID в `.env`.

После обновления `.env`:

```powershell
docker compose up -d --force-recreate n8n
```

Проверить, что webhook установлен:

```powershell
# Не выводить token в консоль. Проверять только host, pending_update_count и last_error_message.
```

Если бот отвечает только стандартной n8n-припиской без полезного текста, сначала проверить, что n8n был пересоздан после импорта workflow и что IF-ветки совпадают с ожидаемыми значениями из раздела выше.

Актуальный workflow отключает n8n attribution для всех Telegram send-узлов. Если приписка снова появляется, переимпортировать workflow и перезапустить n8n.

## Проверка RAG API без Telegram

```powershell
Invoke-RestMethod -Uri 'http://localhost:8000/health'
Invoke-RestMethod -Method Post -Uri 'http://localhost:8000/ask' -ContentType 'application/json' -Body '{"question":"Что говорит статья 70 ТК РФ про испытание?"}'
```

Ожидаемо:

- `refused=false` для вопроса по демо-документам;
- `sources` содержит файл и score;
- `confidence` выше `MIN_CONFIDENCE`.

Контрольный вопрос по исправленному корпусу:

```powershell
Invoke-RestMethod -Method Post -Uri 'http://localhost:8000/ask' -ContentType 'application/json' -Body '{"question":"Сколько может длиться испытательный срок по статье 70 ТК РФ и можно ли его продлить?"}'
```

Ожидаемо: ответ содержит, что продление испытательного срока не допускается.

Direct reply в Telegram:

- `привет`, `/start`, пустой текст и `спасибо` должны отвечать коротким локальным сообщением без вызова `/ask`;
- доменный вопрос должен пройти в `/ask`;
- feedback-кнопки должны пройти в `/feedback`.

## Aviation demo questions (после aviation pass 2026-05-16)

Корпус перепрофилирован под авиагрузовую компанию. Golden-questions для проверки aviation-grounding (`refused=false`, sources указывают на ожидаемый файл, confidence ≥ `MIN_CONFIDENCE`):

```powershell
# 1. Допуск в контролируемую зону аэропорта (ожидается 01_hr_pol_attendance.md или 01_hr_pol_safety.md)
Invoke-RestMethod -Method Post -Uri 'http://localhost:8000/ask' -ContentType 'application/json' -Body '{"question":"Какие условия допуска работника в контролируемую зону аэропорта?"}'

# 2. Aviation security обучение (ожидается 01_hr_pol_training.md или smежные HR policies)
Invoke-RestMethod -Method Post -Uri 'http://localhost:8000/ask' -ContentType 'application/json' -Body '{"question":"Что входит в обязательный инструктаж aviation security для сотрудников грузового терминала?"}'

# 3. Dangerous goods авиаперевозкой (ожидается 05_tlog_regulation_dangerous_goods.md)
Invoke-RestMethod -Method Post -Uri 'http://localhost:8000/ask' -ContentType 'application/json' -Body '{"question":"Какие документы нужны для отправки dangerous goods авиатранспортом?"}'

# 4. AWB/MAWB/HAWB в договоре экспедиции (ожидается 03_legal_contract_expedition*.md)
Invoke-RestMethod -Method Post -Uri 'http://localhost:8000/ask' -ContentType 'application/json' -Body '{"question":"Какие AWB/MAWB/HAWB документы указываются в договоре экспедиции авиагруза?"}'

# 5. Претензия по повреждению авиагруза (ожидается 04_legal_claim_cargo_damage.md)
Invoke-RestMethod -Method Post -Uri 'http://localhost:8000/ask' -ContentType 'application/json' -Body '{"question":"Какие документы нужны для претензии по повреждению авиагруза?"}'

# 6. PDP/коммерческая тайна для AWB и customer data (ожидается 06_comp_policy_pdp.md или comp_policy_data_retention.md)
Invoke-RestMethod -Method Post -Uri 'http://localhost:8000/ask' -ContentType 'application/json' -Body '{"question":"Сколько хранятся AWB, booking и customer data по политике сроков хранения?"}'

# 7. FAQ увольнение сотрудника терминала с пропуском (ожидается 07_faq_dismissal.md)
Invoke-RestMethod -Method Post -Uri 'http://localhost:8000/ask' -ContentType 'application/json' -Body '{"question":"Что делать при увольнении сотрудника грузового терминала с действующим пропуском в контролируемую зону?"}'
```

Для каждого вопроса в ответе должны быть AWB/aviation security/controlled zone/dangerous goods как часть doctype profile, а `sources` — указывать на профильный документ (см. ожидания в комментариях).

## Проверка отказа

Off-corpus refusal — морская перевозка не покрывается aviation corpus:

```powershell
Invoke-RestMethod -Method Post -Uri 'http://localhost:8000/ask' -ContentType 'application/json' -Body '{"question":"Какие правила перевозки лития морем?"}'
```

Ожидаемо:

- `refused=true`;
- ответ сообщает, что источников недостаточно.

Дополнительная проверка: автомобильное first/last mile **входит** в корпус (`07_faq_transport_road.md`, `05_tlog_contract_transport_road.md`), поэтому вопрос про CMR/ТТН на наземном плече **не** должен возвращать refused:

```powershell
Invoke-RestMethod -Method Post -Uri 'http://localhost:8000/ask' -ContentType 'application/json' -Body '{"question":"Какие документы нужны для автомобильного first/last mile авиагруза?"}'
```

## Что показать заказчику

- n8n execution trace по вопросу;
- ответ бота в Telegram;
- наличие whitelist-проверки;
- ответ с источниками и confidence;
- отказ при вопросе вне базы;
- SQL-схему для логов, feedback и review queue.
