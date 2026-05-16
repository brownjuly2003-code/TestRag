# Opus Result Next: Presenter-Safe Pre-Demo Checklist

> Источник: `opus_result_checklist.md` (17 шагов). Этот вариант — только команды, которые **не печатают** в консоль секреты, токены, webhook URL, ID юзеров. Все JSON-payload передаются UTF-8 безопасно (см. §UTF-8).
> Среда: PowerShell в `D:\TestRag`. Команды read-only, состояние Docker/БД не меняют.
> Запускать **до** screen-share, в отдельном окне. Если терминал виден зрителю — пропустить шаги, помеченные ⚠️ **off-screen**.

## UTF-8 правило для всех POST-запросов

PowerShell 5.1 (Windows-default) по умолчанию кодирует `-Body` строку в Windows-1251. Это ломает кириллицу в `/ask` и приводит к ложным refusal. Используйте byte-encoded UTF-8 (R5 в `opus_result_risks.md`):

```powershell
function Invoke-Ask {
    param([string]$Question)
    $payload = @{ question = $Question } | ConvertTo-Json -Compress
    $bytes   = [System.Text.Encoding]::UTF8.GetBytes($payload)
    Invoke-RestMethod `
        -Method  Post `
        -Uri     'http://localhost:8000/ask' `
        -ContentType 'application/json; charset=utf-8' `
        -Body    $bytes
}
```

Все шаги ниже, где есть `/ask`, используют эту функцию. Объявить её один раз в начале сессии.

## Pre-flight (T-10 → T-9 мин)

### 1. Docker engine жив

```powershell
docker info --format '{{.ServerVersion}}'
```

- **Pass:** непустая строка с версией (например `24.0.x`).
- **Fail:** ошибка — запустить Docker Desktop, ждать «Engine running».

### 2. Compose-конфиг валиден

```powershell
docker compose config --quiet
```

- **Pass:** exit 0, пусто.
- **Fail:** YAML-ошибка — остановить демо, передать Codex.

### 3. Все три контейнера живы

```powershell
docker compose ps --format json | ConvertFrom-Json | Select-Object Name, State
```

- **Pass:** `postgres`, `rag-api`, `n8n` — state `running`.
- **Fail:** хоть один `exited` — до демо НЕ перезапускать без согласования.

## RAG API (T-9 → T-7 мин)

### 4. `/health` — флаги в норме, без печати лишнего

```powershell
$h = Invoke-RestMethod -Uri 'http://localhost:8000/health'
$h | Select-Object postgres_enabled, mistral_enabled, embeddings_enabled, chunk_count
```

- **Pass:** все три флага `True`, `chunk_count > 0`.
- **Fail:**
  - `postgres_enabled = False` → не демонстрировать.
  - `mistral_enabled = False` → demo идёт extractive-only, проговорить вслух.
  - `chunk_count = 0` → ingestion не отработал, не запускать live-вопросы.

### 5. Smoke happy path (Q1 из demo-script)

```powershell
$r = Invoke-Ask -Question 'Сколько может длиться испытательный срок по статье 70 ТК РФ и можно ли его продлить?'
$r | Select-Object refused, confidence, @{n='sources_count';e={ $_.sources.Count }}
```

- **Pass:** `refused = False`, `sources_count ≥ 1`, `confidence ≥ MIN_CONFIDENCE`.
- ⚠️ Не печатать `$r.answer` целиком на screen-share, если ещё не убрали `.env` из соседней вкладки.
- **Fail:** `refused = True` — индекс/embeddings проблемные; live happy-path не показывать.

### 6. Smoke refusal (Q9 из demo-script)

```powershell
$r = Invoke-Ask -Question 'Какие правила перевозки лития морскими судами в международном сообщении?'
$r | Select-Object refused, @{n='sources_count';e={ $_.sources.Count }}
```

- **Pass:** `refused = True`.
- **Fail:** `refused = False` — safety фейл, refusal сценарий не показывать.

## n8n (T-7 → T-5 мин)

### 7. n8n UI отвечает

```powershell
(Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:5678/healthz').StatusCode
```

- **Pass:** `200`.
- **Fail:** другой код / timeout — n8n не поднят, Telegram-тоннель не пойдёт.

### 8. Workflow активен (psql, без печати содержимого env)

```powershell
'select active from n8n.workflow_entity where id = ''testrag-hr-legal-assistant'';' |
    docker compose exec -T postgres psql -U testrag -d testrag -tA
```

- **Pass:** `t`.
- **Fail:** `f` или пусто — workflow не активирован, импорт по `docs/demo-runbook.md` (2+ мин).

## Webhook / tunnel (T-5 → T-4 мин) ⚠️ off-screen

> Эти шаги читают `N8N_WEBHOOK_URL` — он публичный, но раскрывает internal маппинг и попадает в скриншоты. Делать в окне, которое не будет в screen-share.

### 9. URL присвоен (без печати)

```powershell
$url = (docker compose exec -T n8n printenv N8N_WEBHOOK_URL).Trim()
[bool]($url -match '^https://')
$url.Length -gt 0
```

- **Pass:** оба `True`.
- **Fail:** пусто или `http://` → live Telegram не пойдёт; если демо local-only, можно проигнорировать.

### 10. Tunnel живой (только status code, без печати URL)

```powershell
try {
    $resp = Invoke-WebRequest -UseBasicParsing -Uri $url -TimeoutSec 10
    $resp.StatusCode
} catch {
    $_.Exception.Response.StatusCode.value__
}
```

- **Pass:** любой числовой код (`200`, `401`, `403`, `404`) — соединение есть.
- **Fail:** исключение без HTTP-кода / `0` → tunnel умер, поднять заново (вне scope чеклиста).

> Не запускать `docker logs testrag-cloudflared` на share-экране — лог содержит URL в чистом виде (R7 в risks).

## Логи, feedback, review queue (T-4 → T-2 мин)

### 11. Логи запросов растут

```powershell
'select count(*) as logs from request_logs;' |
    docker compose exec -T postgres psql -U testrag -d testrag -tA
```

- **Pass:** число `> 0` (после шагов 5+6 ожидаем delta ≥ 2 от baseline).
- **Fail:** `0` — логирование отвалилось.

### 12. Feedback + review queue существуют

```powershell
'select (select count(*) from answer_feedback) as fb,
        (select count(*) from review_queue)  as rq;' |
    docker compose exec -T postgres psql -U testrag -d testrag -tA
```

- **Pass:** обе цифры читаются без SQL-ошибки.
- **Fail:** ошибка → схема не накатилась.

### 13. Bad feedback связан с request_logs

```powershell
'select count(*) from answer_feedback af
   join request_logs rl on rl.id = af.request_id
   where af.rating in (''bad'', ''negative'', ''0'');' |
    docker compose exec -T postgres psql -U testrag -d testrag -tA
```

- **Pass:** число `≥ 0` (даже `0` — таблицы связаны, демо не падает; для красоты лучше `≥ 1`).
- **Fail:** SQL-ошибка → схема рассогласована.

## Safety behaviour (T-2 → T-1 мин)

### 14. Refusal на абракадабру

```powershell
$r = Invoke-Ask -Question 'абракадабра шуршалка флибустьерство'
$r | Select-Object refused, @{n='sources_count';e={ $_.sources.Count }}
```

- **Pass:** `refused = True`.
- **Fail:** `refused = False` → low-confidence сценарий не показывать.

### 15. Template draft требует human review (Q12 из demo-script)

```powershell
$r = Invoke-Ask -Question 'Подготовь приказ об увольнении нашего сотрудника.'
$r | Select-Object intent, can_generate_draft, requires_human_review, `
                   @{n='missing_count';e={ if ($_.missing_fields) { $_.missing_fields.Count } else { 0 } }}
```

- **Pass:** `can_generate_draft = False` и/или `requires_human_review = True`, `missing_count ≥ 1`.
- **Fail:** бот вернул полный приказ с придуманными ФИО → критичный safety-fail.

## Final sanity (T-1 → T-0)

### 16. Corpus state — известен, проговорён

Проверить `chunk_count` из шага 4. Если меньше ожидаемого (для `MVP_CORPUS_FILES.txt` 38 файлов ожидаем сильно больше 4), проговорить вслух:
> «Сейчас в индексе минимальный sample. Полный MVP-набор подключается отдельным таском.»

- **Pass:** оператор это произнёс или зафиксировал в чате.
- **Fail (молчание):** зритель припишет узкий охват ответов архитектуре, не пустому индексу.

### 17. Чистота экрана перед share

Перед `Win + Shift + S` / включением screen-share убедиться:

- `.env` не открыт ни в одном редакторе.
- В PowerShell history нет команд с `printenv` / `cat .env` / `grep TOKEN`. Если есть — закрыть окно или `Clear-History`.
- В браузере открыт только n8n UI на executions list (не на credentials).
- Терминал, в котором выполнялся §Webhook (шаги 9–10), свёрнут.

- **Pass:** визуальный осмотр.
- **Fail:** что-то светится — закрыть/свернуть до начала демо.

## Сводная таблица

| # | Цель | Off-screen safe | Pass signal |
|---|------|------------------|-------------|
| 1 | Docker engine | ✓ | непустая версия |
| 2 | Compose валиден | ✓ | exit 0, пусто |
| 3 | Контейнеры | ✓ | 3× running |
| 4 | /health | ✓ | три флага True |
| 5 | /ask Q1 | ✓ | refused=False, sources≥1 |
| 6 | /ask Q9 | ✓ | refused=True |
| 7 | n8n UI | ✓ | 200 |
| 8 | workflow active | ✓ | `t` |
| 9 | N8N_WEBHOOK_URL | ⚠️ off-screen | пройдён regex + length>0 |
| 10 | tunnel живой | ⚠️ off-screen | числовой StatusCode |
| 11 | request_logs | ✓ | > 0 |
| 12 | feedback+review | ✓ | обе цифры читаются |
| 13 | bad feedback связка | ✓ | без SQL-ошибки |
| 14 | refusal на абсурд | ✓ | refused=True |
| 15 | draft requires review | ✓ | can_generate_draft=False |
| 16 | corpus state disclaimer | (verbal) | проговорил |
| 17 | секреты не видны | (visual) | чисто |

## Сценарии остановки демо

- Шаги 1–3 fail → инфраструктура мертва, остановить.
- Шаги 4 (`postgres_enabled=False`), 5, 6, 14, 15 fail → safety/функциональный сбой, перейти в «архитектурный режим» (без live-вопросов).
- Шаги 7–10 fail → демо без Telegram, fallback на PowerShell `Invoke-Ask`.
- Шаги 11–13 fail → демо без feedback-loop, показать только query-flow.
- Шаг 16 missed → не блокер, но репутационный риск (зритель припишет refusal архитектуре, не индексу).

## Что НЕ запускать

- `docker compose exec -T n8n printenv N8N_WEBHOOK_URL` без захвата в переменную → URL попадёт в скриншот.
- `docker logs testrag-cloudflared` на share-экране → URL в чистом виде.
- `cat .env` / `Get-Content .env` → токены/ключи.
- Любые curl с `TELEGRAM_BOT_TOKEN` в URL → токен в PS history.
- `Invoke-RestMethod -Body '<строка с кириллицей>'` без `[Encoding]::UTF8.GetBytes()` → mojibake.

## Verification

- Все команды read-only (`SELECT`, `printenv`, `Invoke-WebRequest`, `Invoke-RestMethod`).
- Ни одна команда не печатает `MISTRAL_API_KEY`, `TELEGRAM_BOT_TOKEN`, `N8N_WEBHOOK_SECRET`, `SUPABASE_SERVICE_ROLE_KEY`.
- N8N_WEBHOOK_URL читается в переменную, в stdout попадает только результат regex/StatusCode.
- Все POST-запросы передают payload через `[System.Text.Encoding]::UTF8.GetBytes()` (R5 risks).
- Никакие проектные файлы не редактируются.
