# Opus Result Followup: Risk Burn-Down

> Baseline: `opus_result_risks.md` (12 ranked risks).
> Изменения с прошлого паса: Codex обновил manifest до 38 файлов, `chunk_count=122`, `documents=42`; синхронизировал термины в Mermaid; теперь владеет live Telegram/n8n routing; `MVP_CORPUS_FILES.txt` подключён к ingestion.
> Назначение: что осталось из риска, кому это адресовано, и go/no-go сигнал за 10 минут до демо.
> Никакие правки в `corpus/`, `rag-api/`, `docs/`, `manifests/`, `.env*`, `docker-compose.yml`, `mvp-plan.md`, `README.md` не делались. Live-проверки не запускались.

## Burned-down (закрыто/значительно снижено)

| # | Original | Score было | Score стало | Что закрыло |
|---|----------|-----------|-------------|--------------|
| R3 | Low source coverage (4 чанка) | 16 | 0–2 | `chunk_count=122`, `documents=42` после ingestion MVP-корпуса; 10/12 demo-вопросов уже PASS (Q6, Q8 закрываются после применения swap из `opus_result_followup_manifest_decision.md`). |
| R5 | PowerShell UTF-8 / кириллица | 12 | 2 | `opus_result_next_presenter_checklist.md §UTF-8` даёт `Invoke-Ask` функцию с byte-encoded payload. Закрыто при условии, что оператор использует presenter-чеклист, а не runbook напрямую. |

## Partial (часть закрыта, часть остаётся)

| # | Original | Score было | Score стало | Что закрыто / что остаётся |
|---|----------|-----------|-------------|----------------------------|
| R2 | Missing whitelist | 16 | 8 | Closed: whitelist настроен для `432751211` (mvp-plan §Current Status). Open: если зритель попросит «попробовать с моего аккаунта» — переключение требует `.env` правки + `docker compose up -d --force-recreate n8n` на share-экране. |
| R7 | trycloudflare URL leaks via screen-share | 9 | 4 | Closed (если применят P5 docs-patch): добавлена warning-аннотация про screen-share. Open: оператор должен фактически следовать аннотации. |
| R10 | Supabase vs Postgres docs mismatch | 6 | 3 | Closed: Mermaid диаграммы переименованы. Open: `README §Конфигурация` всё ещё содержит `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` — закроется патчем P1 из `opus_result_followup_docs_patch_plan.md`. |

## Active (требуют действия до демо)

### A1. Stale tunnel URL (бывший R1, Score 25)

**Сценарий:** trycloudflare-URL меняется при каждом перезапуске контейнера `testrag-cloudflared`. На демо-нагрузке (часовой подъём Docker, sleep ноута) URL может умереть; n8n будет писать в актуальный URL только если он обновлён в `.env` и контейнер пересоздан.

**Owner:** Codex (он же владеет fix live Telegram/n8n routing).

**Mitigation:**
1. За **час до демо** пересоздать tunnel; записать актуальный URL в `.env`; пересоздать `n8n` через `docker compose up -d --force-recreate n8n`; через BotFather `setWebhook` обновить.
2. Не запускать `docker logs testrag-cloudflared` на share-экране (см. R7).
3. План Б: presenter-чеклист §10 проверяет StatusCode tunnel-URL без печати URL.

**Residual exposure:** L4 × I5 = 20 (снижение Score с 25 до 20 только за счёт известного процесса; сам tunnel-URL пересоздавать всё равно придётся).

### A2. Post-swap re-ingestion timing (новый, Score 16)

**Сценарий:** `opus_result_followup_manifest_decision.md` рекомендует swap 4 in / 4 out, в т.ч. добавление `05_tlog_regulation_cmr.md` (для Q6) и `06_comp_policy_nda_employee.md` (для Q8). Без применения swap demo-script содержит вопросы (Q7, Q8 если расширить, потенциально Q6 в reserve), которые не покроются. Если Codex применяет swap, но не успевает re-ingest до демо — `/health` `chunk_count` не отражает новые файлы.

**Owner:** Codex.

**Mitigation:**
1. Применить swap **не позже T-1 час** до демо.
2. После применения: `docker compose up -d --force-recreate rag-api` (полное переиндексирование) ИЛИ инкрементальный ingest для 4 добавленных + delete-orphan для 4 удалённых.
3. Pre-demo gate в `opus_result_next_presenter_checklist.md §5` тестирует Q1; для уверенности также прогнать Q6 (CMR) и Q8 (commercial secret + NDA employee) офлайн через `Invoke-Ask`.

**Residual exposure:** L4 × I4 = 16.

### A3. Synthetic-corpus disclaimer не в коде (бывший R4, Score 12)

**Сценарий:** `manifests/MANIFEST.md §header` фиксирует synthetic origin, но **в текущем API-ответе** disclaimer не присутствует (не виден из доступных в read-only режиме файлов; вне Opus scope для проверки кода). Зритель может процитировать политику как корпоративную норму.

**Owner:** Codex (имплементация), Demo operator (verbal disclaimer как страховка).

**Mitigation:**
1. Codex: вставить постфикс из `opus_result_followup_telegram_copy.md §6A` в каждый ответ `/ask`. Для template_draft — §6B.
2. Demo operator: проговорить «корпус демо, нормативные ссылки реальные» один раз в начале + перед Q11 (template_draft).
3. Слайд-disclaimer из `opus_result_next_disclaimer.md` на отдельном слайде до live questions.

**Residual exposure:** L2 × I4 = 8 после применения 1+2.

### A4. Legal disclaimer gap on template_draft (бывший R6, Score 12)

**Сценарий:** `docs/legal-document-prompts.md` требует пометку «Требует проверки HR/юристом» на черновиках. Без её фактического присутствия в `answer` или `draft` поле зритель может расценить вывод как готовый документ. Q11 — самый опасный сценарий.

**Owner:** Codex.

**Mitigation:**
1. Verify presenter checklist §15 (template_draft возвращает `requires_human_review=true`).
2. Если флага нет — Codex добавить в response schema поле `requires_human_review: bool` и заполнять `true` всегда для intent в {template_draft, document_type_detection, field_collection}.
3. Если поле есть, но не маппится в Telegram-текст — Codex применить §6B из telegram_copy.

**Residual exposure:** L3 × I4 = 12 (без подтверждения кода — не можем снизить).

### A5. Refusal wording звучит как «бот не работает» (бывший R8, Score 8)

**Сценарий:** Refusal-сообщение, если короткое («недостаточно источников»), читается как поломка.

**Owner:** Codex.

**Mitigation:**
1. Заменить дефолтный refusal-текст RAG API на §2 из `opus_result_followup_telegram_copy.md` (varianty A/B/C по контексту).
2. Demo operator: перед Q9 проговорить «это safety-сценарий, мы намеренно проверяем отказ».

**Residual exposure:** L3 × I2 = 6 после wording-патча.

### A6. Refusal не записывается в request_logs (бывший R9, Score 8)

**Сценарий:** Чеклист §11 проверяет рост `request_logs`. Если RAG API делает early return до записи на `refused=true`, демо-вопросы Q9, Q14 не попадут в логи → шаг 11 покажет, что счётчик не растёт.

**Owner:** Codex.

**Mitigation:**
1. Codex: подтвердить, что `request_logs` пишется в **любом** ответе, включая refused.
2. Demo operator: запустить чеклист §11 **до и после** Q1 (которого refused=false) и Q9 (refused=true) — посмотреть delta. Если delta=1 (а не 2) — refusal не пишется.

**Residual exposure:** L2 × I3 = 6 (impact снижен — это не safety, это аналитика).

### A7. Бесконтрольные ingestion-events во время демо (бывший R11, Score 4)

**Сценарий:** Codex применяет swap или recompiles индекс в окно демо → ответы «дёрнутся».

**Owner:** Codex (coordination), Demo operator.

**Mitigation:** Codex явно подтверждает в чате: «никаких ingestion в окне T-15 → T+30 от demo». Это договорное, не техническое.

**Residual exposure:** L1 × I2 = 2 после координации.

## Сводная таблица (post-Codex)

| Rank | Risk | Owner | Score было | Score стало | Status |
|------|------|-------|-----------|-------------|--------|
| 1 | A1 Stale tunnel | Codex + Operator | 25 | 20 | ACTIVE |
| 2 | A2 Post-swap re-ingestion | Codex | — | 16 | NEW |
| 3 | A4 Legal disclaimer gap | Codex | 12 | 12 | ACTIVE pending code |
| 4 | A3 Synthetic disclaimer not in answer | Codex + Operator | 12 | 8 | ACTIVE pending code |
| 5 | R2 Whitelist coverage | Operator | 16 | 8 | PARTIAL |
| 6 | A5 Refusal wording dry | Codex | 8 | 6 | ACTIVE pending code |
| 7 | A6 Refusal not in logs | Codex | 8 | 6 | UNKNOWN, нужна сверка |
| 8 | R7 trycloudflare leaks | Operator | 9 | 4 | PARTIAL (после P5 patch) |
| 9 | R10 Supabase docs | Codex | 6 | 3 | PARTIAL (после P1 patch) |
| 10 | A7 Ingestion during demo | Codex | 4 | 2 | ACTIVE (coordination) |
| 11 | R3 Low coverage | — | 16 | 0–2 | BURNED |
| 12 | R5 PowerShell UTF-8 | Operator | 12 | 2 | BURNED |
| 13 | R12 MANIFEST size | Operator | 3 | 1 | inactive |

Top-5 после burn-down: **A1, A2, A4, A3, R2.**

## 10-минутный go/no-go signal (T-10 → T-0)

Эти 10 проверок дают бинарное «можно демо / нет». Все команды read-only, безопасны на screen-share при условии presenter-чеклиста.

### GO conditions (все должны быть true)

| # | Проверка | Команда / источник | GO signal |
|---|----------|--------------------|-----------|
| G1 | RAG API жив | `Invoke-RestMethod 'http://localhost:8000/health'` | `postgres_enabled=True`, `mistral_enabled=True`, `embeddings_enabled=True` |
| G2 | Manifest swap применён | `(Invoke-RestMethod 'http://localhost:8000/health').chunk_count` | `chunk_count > 120` (точное число зависит от chunk_size) |
| G3 | Q1 happy path | `Invoke-Ask -Question '...статья 70...'` | `refused=False`, `sources.Count >= 1` |
| G4 | Q9 refusal | `Invoke-Ask -Question '...лития морскими...'` | `refused=True` |
| G5 | Q11 draft требует review | `Invoke-Ask -Question 'Подготовь черновик приказа о приёме...'` | `requires_human_review=True` ИЛИ текст «Требует проверки» |
| G6 | n8n workflow active | `psql workflow_entity where id='testrag-hr-legal-assistant'` | `active = t` |
| G7 | Tunnel жив | `Invoke-WebRequest $tunnel_url; .StatusCode` | числовой код (любой 2xx/4xx) |
| G8 | request_logs пишется | `select count(*) from request_logs;` до и после G3 | delta ≥ 1 |
| G9 | Whitelist настроен на оператора demo | сравнить `ALLOWED_TELEGRAM_USER_IDS` с ID, который будет писать (off-screen) | оператор в списке |
| G10 | Disclaimer виден в ответе | в `$r.answer` после G3 присутствует «демо» / «не юридическая консультация» / «синтетический» | хотя бы один маркер |

### NO-GO triggers (любой → не показывать live)

| Trigger | Что делать |
|---------|------------|
| G1 fail (`postgres_enabled=False`) | Демо невозможен. Отложить или показать только архитектуру по README. |
| G2 fail (`chunk_count < 50`) | Manifest не подтянулся → большинство вопросов уйдёт в refusal. Перенести демо. |
| G3 fail | Q1 не работает на свежем индексе. Опросить Codex (issue с retrieval). Демо в архитектурном режиме. |
| G4 fail (refused=False на «литий морем») | **Safety regression**. Не показывать live. Объяснить как known issue. |
| G5 fail | Template_draft не безопасный. Не запускать Q11 — пропустить, демо короче. |
| G6 fail | Telegram не пойдёт через workflow. Демо через PowerShell `Invoke-Ask` без Telegram. |
| G7 fail | Live Telegram не доступен. Аналогично G6. |
| G10 fail | Disclaimer не виден. Демо идёт, но **оператор обязан** проговорить устный disclaimer (см. `opus_result_next_disclaimer.md §4`). |

### Soft warnings (демо идёт, но с оговорками)

| Warning | Operator response |
|---------|--------------------|
| G2: 50 ≤ `chunk_count` ≤ 120 | «Sample shortlist, полный корпус — следующий таск». |
| G5: флаг `requires_human_review` отсутствует, но в тексте есть пометка | OK для демо, но запросить Codex добавить флаг. |
| G8: delta = 0 после G3 | Refusal в request_logs не пишется. Снять из demo §request_logs, не показывать счётчик. |

## Если что-то падает в T-2 → T-0

| Время до старта | Действие |
|-----------------|----------|
| T-2 мин: G1/G2 fail | Отменить live, начать с архитектуры. |
| T-1 мин: G3/G4/G5 fail | Удалить соответствующий вопрос из demo-script. |
| T-30 сек: G7 fail | Переключиться на PowerShell `Invoke-Ask` через share-экран (заранее заготовить терминал). |
| T-0: всё ок | Запустить demo по `opus_result_next_demo_script.md` Шаг 1. |

## Что не покрыто этим burn-down

- Performance под нагрузкой (multi-user) — out of scope MVP.
- GDPR / privacy при live Telegram-сообщениях зрителей — нужен письменный consent перед демо, не в коде.
- Безопасность n8n credentials — за рамками `corpus/`, не открывали.

## Verification (self-check)

- 12 original риска переоценены поштучно. 2 burned, 3 partial, 7 active.
- 1 новый risk (A2 re-ingestion) добавлен с обоснованием.
- Каждый active risk имеет owner ∈ {Codex, Operator}.
- 10-минутный go/no-go даёт чёткие пороги, привязанные к проверкам из `opus_result_next_presenter_checklist.md`.
- Никаких live-проверок не выполнялось. Проектные файлы не редактировались.
