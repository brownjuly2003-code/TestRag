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

## Локальный Telegram Webhook

Telegram не отправляет webhook на `localhost`. Для live-demo нужен публичный HTTPS tunnel:

- Cloudflare Tunnel;
- ngrok;
- другой временный HTTPS endpoint.

После получения HTTPS URL записать его в `.env`:

```env
N8N_WEBHOOK_URL=https://your-tunnel-url/
```

Затем перезапустить n8n:

```powershell
docker compose up -d n8n
```

Для быстрого временного tunnel можно использовать Cloudflare Tunnel в Docker:

```powershell
docker run -d --name testrag-cloudflared --network testrag_default cloudflare/cloudflared:latest tunnel --no-autoupdate --url http://n8n:5678
docker logs testrag-cloudflared
```

В логах найти URL вида `https://...trycloudflare.com`, записать его в `N8N_WEBHOOK_URL` и перезапустить n8n.

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

## Проверка отказа

```powershell
Invoke-RestMethod -Method Post -Uri 'http://localhost:8000/ask' -ContentType 'application/json' -Body '{"question":"Какие правила перевозки лития морем?"}'
```

Ожидаемо:

- `refused=true`;
- ответ сообщает, что источников недостаточно.

## Что показать заказчику

- n8n execution trace по вопросу;
- ответ бота в Telegram;
- наличие whitelist-проверки;
- ответ с источниками и confidence;
- отказ при вопросе вне базы;
- SQL-схему для логов, feedback и review queue.
