# Opus Result: Pre-Demo Acceptance Checklist (10 минут)

> Назначение: за 10 минут до демо проверить, что все компоненты живы и поведение совпадает с MVP-критериями.
> Источники: `README.md`, `mvp-plan.md`, `docs/demo-runbook.md`, `docs/legal-document-prompts.md`.
> Запуск: PowerShell в `D:\TestRag`.
> Все команды read-only или не меняют состояние Docker/БД.

## Pre-flight (T-10 → T-9 мин)

### 1. Docker Desktop запущен

```powershell
docker info --format '{{.ServerVersion}}'
```

- **Expected:** одна непустая строка с версией (например `24.0.x`).
- **Pass:** строка с версией.
- **Fail:** ошибка `dockerDesktopLinuxEngine` → запустить Docker Desktop вручную, ждать «Engine running».

### 2. Compose-конфиг валиден

```powershell
docker compose config --quiet
```

- **Expected:** нет вывода (exit 0).
- **Pass:** пустой stdout/stderr.
- **Fail:** YAML-ошибка → не трогать, остановить демо, передать Codex.

### 3. Все три контейнера живы

```powershell
docker compose ps --format json
```

- **Expected:** три сервиса `postgres`, `rag-api`, `n8n` в state `running` или `healthy`.
- **Pass:** `state=running` для всех трёх.
- **Fail:** хотя бы один `exited` → `docker compose logs <service> --tail=50` (read-only) и решать; до демо НЕ перезапускать без согласования.

---

## RAG API (T-9 → T-7 мин)

### 4. `/health` отвечает и флаги в норме

```powershell
Invoke-RestMethod -Uri 'http://localhost:8000/health' | ConvertTo-Json -Depth 5
```

- **Expected (по `mvp-plan.md §Current Status`):**
  - `postgres_enabled = true`
  - `mistral_enabled = true`
  - `embeddings_enabled = true`
  - `chunk_count` ≥ 4 (для shortlist ≥ 30 файлов ожидать сильно больше)
- **Pass:** все три флага `true` и `chunk_count > 0`.
- **Fail:**
  - `postgres_enabled=false` → Postgres недоступен, не демонстрировать.
  - `mistral_enabled=false` → демо пойдёт extractive-only, упомянуть это вслух или не показывать вопросы с MEDIUM/LOW confidence.
  - `chunk_count=0` → ingestion не отработал, не демонстрировать happy-path.

### 5. Smoke-вопрос (happy path)

```powershell
$body = '{"question":"Что говорит статья 70 ТК РФ про испытание?"}'
Invoke-RestMethod -Method Post -Uri 'http://localhost:8000/ask' -ContentType 'application/json' -Body $body | ConvertTo-Json -Depth 5
```

- **Expected:**
  - `refused = false`
  - `sources` — массив длиной ≥ 1
  - `confidence` ≥ `MIN_CONFIDENCE` (значение из API; обычно > 0.3)
  - `answer` непустой, содержит «3 мес» или «70»
- **Pass:** все четыре условия.
- **Fail:** если `refused=true` на этом вопросе — проблема с индексом / embeddings; не демонстрировать live, объяснить.

### 6. Smoke-вопрос (refusal)

```powershell
$body = '{"question":"Какие правила перевозки лития морем?"}'
Invoke-RestMethod -Method Post -Uri 'http://localhost:8000/ask' -ContentType 'application/json' -Body $body | ConvertTo-Json -Depth 5
```

- **Expected:**
  - `refused = true`
  - `answer` содержит формулировку «недостаточно источников» / «уточните вопрос»
  - `sources` пустой или с пометкой низкой уверенности
- **Pass:** `refused=true`.
- **Fail:** если `refused=false` — модель «галлюцинирует» по out-of-scope вопросу; критично для демо («safe RAG»), не показывать.

---

## n8n (T-7 → T-5 мин)

### 7. n8n UI доступен

```powershell
Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:5678/healthz' | Select-Object StatusCode
```

- **Expected:** `StatusCode = 200`.
- **Pass:** 200.
- **Fail:** не 200 — n8n не поднялся, тоннель работать не будет.

### 8. Workflow активен в базе

```powershell
'select id, name, active from n8n.workflow_entity;' | docker compose exec -T postgres psql -U testrag -d testrag
```

- **Expected:** хотя бы одна строка `id=testrag-hr-legal-assistant`, `active=t`.
- **Pass:** строка есть и `active=t`.
- **Fail:** `active=f` или нет записи → импортировать workflow по `docs/demo-runbook.md §«Импорт n8n Через CLI»` (но обычно это занимает > 2 минут — не успеть в 10-минутный план).

---

## Webhook / tunnel (T-5 → T-4 мин)

### 9. `N8N_WEBHOOK_URL` присвоен и HTTPS

```powershell
docker compose exec -T n8n printenv N8N_WEBHOOK_URL
```

- **Expected:** строка, начинающаяся с `https://`, оканчивается на `/` (например `https://abc-xyz.trycloudflare.com/`).
- **Pass:** валидный HTTPS URL.
- **Fail:** пусто или `http://` → live Telegram не пойдёт. Если демо только локальное (без Telegram), можно проигнорировать.

### 10. Tunnel живой (без печати tokens)

```powershell
Invoke-WebRequest -UseBasicParsing -Uri (docker compose exec -T n8n printenv N8N_WEBHOOK_URL) | Select-Object StatusCode
```

- **Expected:** `StatusCode ∈ {200, 401, 403, 404}` — главное, что соединение есть.
- **Pass:** любой response code (не timeout, не DNS-fail).
- **Fail:** timeout / connection refused → tunnel умер, поднять заново (вне scope этого чеклиста).

> Важно: НЕ печатать `TELEGRAM_BOT_TOKEN` ни в одной команде. Если нужно проверить webhook у Telegram — использовать запрос с токеном **только** в hidden шаге через переменную окружения, и НЕ выводить URL в консоль (см. `docs/demo-runbook.md` line 86 предупреждение).

---

## Логи, feedback и review queue (T-4 → T-2 мин)

### 11. Логи запросов растут

```powershell
'select count(*) as logs, max(created_at) as last_at from request_logs;' | docker compose exec -T postgres psql -U testrag -d testrag
```

- **Expected:** `logs ≥ 11` (после шагов 5+6 должно быть `≥ 13`), `last_at` — последние минуты.
- **Pass:** число > 0 и недавнее `last_at`.
- **Fail:** `logs=0` — логирование отвалилось.

### 12. Feedback таблица и review queue существуют и пишутся

```powershell
'select count(*) as feedback_rows from answer_feedback; select count(*) as review_rows from review_queue;' | docker compose exec -T postgres psql -U testrag -d testrag
```

- **Expected:** обе таблицы существуют. `mvp-plan.md` указывает baseline `answer_feedback=1`, `review_queue=1` — числа должны быть ≥ baseline.
- **Pass:** обе таблицы возвращают `count >= 0` без ошибки и хотя бы одна > 0 (демо-зрителю показывается, что pipeline сработал хоть раз).
- **Fail:** ошибка SQL → схема не накатилась, не демонстрировать feedback flow.

### 13. Bad feedback пишет в review_queue (smoke, без вызова API)

```powershell
'select rl.id, rl.question, af.rating from request_logs rl join answer_feedback af on af.request_id = rl.id where af.rating in (''bad'',''negative'',0) limit 1;' | docker compose exec -T postgres psql -U testrag -d testrag
```

- **Expected:** хотя бы одна строка (для demo-видимости связки).
- **Pass:** строка есть.
- **Fail:** пусто — bad feedback ни разу не приходил; решение зависит от того, насколько критично показать review-queue зрителю. Можно вручную добавить через UI Telegram во время демо.

---

## Refusal behaviour & legal disclaimer (T-2 → T-1 мин)

### 14. Refusal-policy включена

```powershell
$body = '{"question":"абракадабра"}'
Invoke-RestMethod -Method Post -Uri 'http://localhost:8000/ask' -ContentType 'application/json' -Body $body | ConvertTo-Json -Depth 3
```

- **Expected:** `refused=true`, `sources` пустые или с пометкой «недостаточно».
- **Pass:** `refused=true`.
- **Fail:** `refused=false` или 500 → не показывать low-confidence сценарий.

### 15. Template draft возвращает требование human review

```powershell
$body = '{"question":"Подготовь приказ об увольнении нашего сотрудника."}'
Invoke-RestMethod -Method Post -Uri 'http://localhost:8000/ask' -ContentType 'application/json' -Body $body | ConvertTo-Json -Depth 5
```

- **Expected:** структура содержит `requires_human_review = true` (или эквивалентный флаг, согласно `docs/legal-document-prompts.md`); `can_generate_draft = false` (ФИО/основание не переданы); `missing_fields` — непустой массив; intent — `field_collection` или `document_type_detection`.
- **Pass:** ни одного «свободно сгенерированного» полного приказа.
- **Fail:** API вернул полный текст приказа с придуманными ФИО / датами → критичный safety-fail, не показывать.

---

## Final sanity (T-1 → T-0)

### 16. Подсветка факта: текущий corpus — sample (4 чанка)

Если `chunk_count` в шаге 4 был ~4, явно проговорить зрителю до demo:
> «В текущей сборке проиндексирован минимальный sample (4 чанка). Полный shortlist из MVP-корпуса (≈30 файлов) подключается отдельным таском (см. `mvp-plan.md §Next Tasks`).»

- **Pass:** оператор это произнёс или зафиксировал в чате.
- **Fail:** если умолчать, зритель припишет узкий охват ответов архитектуре, а не «недозалитому корпусу».

### 17. Все вкладки/окна закрыты, секреты не отображаются

- **Expected:** в браузере открыт только n8n UI без раскрытых credentials; PowerShell history не содержит `printenv TELEGRAM_BOT_TOKEN`; `.env` не открыт ни в одном редакторе.
- **Pass:** визуальный осмотр.
- **Fail:** что-то светится — закрыть/свернуть до начала демо.

---

## Сводная таблица (для быстрого прогона)

| # | Цель | Команда (PowerShell) | Pass signal |
|---|------|----------------------|-------------|
| 1 | Docker engine | `docker info --format '{{.ServerVersion}}'` | непустая версия |
| 2 | Compose валиден | `docker compose config --quiet` | exit 0, пусто |
| 3 | Контейнеры | `docker compose ps --format json` | 3× running |
| 4 | /health | `Invoke-RestMethod 'http://localhost:8000/health'` | три флага true |
| 5 | /ask happy | `…/ask` ст.70 ТК | `refused=false`, sources≥1 |
| 6 | /ask refusal | `…/ask` литий морем | `refused=true` |
| 7 | n8n UI | `Invoke-WebRequest 'http://localhost:5678/healthz'` | 200 |
| 8 | workflow active | `psql workflow_entity` | active=t |
| 9 | N8N_WEBHOOK_URL | `docker compose exec n8n printenv N8N_WEBHOOK_URL` | https://… |
| 10 | tunnel живой | `Invoke-WebRequest $N8N_WEBHOOK_URL` | StatusCode 200/40x |
| 11 | request_logs | `psql count(*)` | > 0 |
| 12 | feedback+review | `psql count(*)` | обе таблицы есть |
| 13 | bad feedback связка | `psql join request_logs+answer_feedback` | ≥ 1 строка |
| 14 | refusal на абсурд | `…/ask` абракадабра | `refused=true` |
| 15 | draft requires review | `…/ask` приказ об увольнении | `requires_human_review=true` |
| 16 | corpus size disclaimer | (verbal) | сказано |
| 17 | секреты не видны | (visual) | чисто |

## Сценарии остановки демо

- Шаги 1, 2, 3 fail → инфраструктура мертва, демо невозможно. Останов.
- Шаги 4 (`postgres_enabled=false`), 5 (smoke fail), 14 (refusal fail), 15 (draft fail) → safety-сбой, демо нерепрезентативно. Останов или demo «только архитектура без live-вопросов».
- Шаги 7, 8, 9, 10 fail → демо без Telegram, можно показать в Postman / PowerShell вызовы API напрямую (как fallback).
- Шаги 11, 12, 13 fail → демо без feedback-loop; показать только query-flow.
- Шаг 16 missed (не проговорил corpus state) — не блокер, но репутационный риск.
