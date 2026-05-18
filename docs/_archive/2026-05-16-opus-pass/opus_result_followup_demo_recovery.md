# Opus Result Followup: Demo Recovery Plan

> Status 2026-05-16: The greeting path is fixed and verified at T0 level for the observed issue. Keep this recovery plan as a fallback runbook for future demo windows.

> Контекст: Telegram-бот молчит на `привет`. Codex чинит, но может не успеть до демо. План — на случай, если на T-0 Telegram-путь нестабилен.
> Источники: `opus_result_followup_greeting_route_triage.md`, `opus_result_followup_silent_bot_checklist.md`, `opus_result_followup_risk_burndown.md`.
> Назначение: 10-минутный go/no-go + presenter fallback wording + минимальное приемлемое поведение, если greeting путь сломан.
> Никакие файлы не редактировались.

## Уровни «приемлемости» демо (downgrade ladder)

Чем ниже tier — тем меньше зависит от живого Telegram. Operator должен заранее знать, на каком tier'е сейчас система.

| Tier | Что работает | Что показываем | Что говорим зрителю |
|------|--------------|----------------|----------------------|
| **T0 — Full live** | Greeting (после Codex fix) + 6 demo вопросов + feedback + Telegram | Telegram-чат с зрителем или с самим собой | «Это live-бот: задаю вопрос — бот отвечает с источниками.» |
| **T1 — Live, без greeting** | 6 demo вопросов работают, но на `привет` нет ответа | Telegram-чат, но **только** domain-вопросы | «На приветствия пока в работе — показываю содержательные запросы.» |
| **T2 — Live API, без Telegram** | RAG API через PowerShell `Invoke-Ask` | Терминал с byte-encoded JSON-запросами | «Telegram-маршрут перенастраиваем — показываю прямые вызовы API. Та же логика, тот же ответ.» |
| **T3 — Только архитектура** | Ничего не работает live; есть `/health` | README + Mermaid + результаты `pytest` + executions из прошлых сессий | «Сегодня показываю архитектуру и метрики. Live-демо — на следующей встрече.» |

Цель — **никогда не падать ниже T2** во время демо. T3 — последний рубеж и его нужно держать готовым.

## 10-минутный go/no-go (T-10 → T-0)

Расширенная версия чеклиста из `opus_result_followup_risk_burndown.md §10-минутный go/no-go signal`, специально под инцидент «привет → silence».

### T-10 → T-8 мин: инфра

| # | Команда | Pass = T0 | Fail = downgrade |
|---|---------|-----------|------------------|
| G1 | `Invoke-RestMethod 'http://localhost:8000/health'` | три флага `True`, `chunk_count > 100` | flags=False → T3; chunk_count=0 → T3 |
| G2 | `docker compose ps --format json \| ConvertFrom-Json` | postgres/rag-api/n8n state=running | n8n down → T2; rag-api down → T3 |
| G3 | `(Invoke-WebRequest http://localhost:5678/healthz).StatusCode` | 200 | не 200 → T2 |

### T-8 → T-5 мин: greeting smoke

> Codex должен подтвердить за час до демо, применил ли он fix T1.1–T1.3 + T2.1 из `opus_result_followup_telegram_regression_spec.md`. Если **да** — все G4–G7 имеют шанс быть T0. Если **нет** — заранее downgrade до T1.

| # | Команда | Pass = T0 | Fail = T1 |
|---|---------|-----------|------------|
| G4 | `Invoke-Ask -Question 'привет'` (см. UTF-8 byte-encoding в presenter_checklist) | 200, `answer` непустой, `refused=true` или greeting text | empty answer / 5xx → T1 |
| G5 | `Invoke-Ask -Question 'Сколько длится испытательный срок?'` | 200, `refused=false`, sources ≥ 1, упоминание «3 мес» / «70» | → T2 если refusal или sources=0 |
| G6 | `Invoke-Ask -Question 'Какие правила перевозки лития морскими судами?'` | `refused=true` | если refused=false → safety regression, не показывать Q9 live |
| G7 | Off-screen: тест-сообщение `привет` со своего Telegram | бот отвечает текстом в Telegram | нет ответа за 5 сек → T1 (без greeting) или T2 (вообще без Telegram) |

### T-5 → T-3 мин: проверка fallback-пути

| # | Команда | Pass | Fail |
|---|---------|------|------|
| G8 | Off-screen: domain вопрос в Telegram («Сколько длится испытательный срок?») | бот отвечает с источниками | если нет ответа но G4–G6 ok → T2 (только PS) |
| G9 | Off-screen: feedback Good на ответе из G8 | бот пишет «Оценка принята.» | не критично, soft warning |
| G10 | psql `select count(*) from request_logs where created_at > now() - interval '5 minutes';` | ≥ 2 (G4 + G5) | если 0 → /ask не пишет логи; T2 без счётчика |

### T-3 → T-1 мин: presenter setup

| # | Что | Готово? |
|---|-----|---------|
| G11 | Окно с PS уже открыто, `Invoke-Ask` функция определена | ☐ |
| G12 | Окно с Telegram чатом открыто (если ≥ T1) | ☐ |
| G13 | Браузер на executions n8n (off-screen tab) | ☐ |
| G14 | Слайды с диаграммой архитектуры — открыты | ☐ |
| G15 | `.env`, terminal history со словом TOKEN — закрыты | ☐ |
| G16 | trycloudflare URL — НЕ виден на экране | ☐ |

### T-1 → T-0: final tier decision

| Условие | Tier |
|---------|------|
| G1–G3 ok, G4–G7 ok | **T0 — full live** |
| G1–G3 ok, G4 ok (greeting), G5 ok, G7 ok | **T0** |
| G1–G3 ok, G5 ok, G7 ok, G4 fail | **T1 — без greeting** |
| G1–G3 ok, G5 ok, G7 fail | **T2 — PS only** |
| G5 fail | **T3 — только архитектура** |

Тier фиксируется к T-0 и не меняется в процессе демо.

---

## Presenter fallback wording (по tier)

### T0 (full live) — стандартный open

```
Покажу демо HR/legal RAG-ассистента. Сейчас задам несколько вопросов в Telegram — увидите ответы с источниками, отказ на off-topic, и черновик документа.

Сразу обозначу: документы корпуса — синтетические образцы для демо, нормативные ссылки реальные. Это не юридическая консультация.
```

### T1 (live без greeting) — мягкий downgrade

```
Покажу демо. Один уточняющий момент: small-talk (приветствия) обрабатываем отдельно от content-запросов, и это сейчас в финальной шлифовке. Сегодня сосредоточусь на содержательных вопросах — они проходят по всему пайплайну.

Документы корпуса синтетические, нормативные ссылки реальные.
```

### T2 (PS only) — открытый downgrade

```
Покажу демо. Telegram-маршрут сегодня перенастраиваем, поэтому буду обращаться к API напрямую через PowerShell — это тот же контур, что у бота, только без Telegram-обвязки. Запрос → классификация → hybrid retrieval → ответ с источниками — увидите ровно то же поведение.

Документы корпуса синтетические, нормативные ссылки реальные.
```

### T3 (только архитектура) — честный downgrade

```
Сегодня покажу архитектуру и метрики, а живой прогон вопросов — на следующей встрече. Причина: один из инфраструктурных компонентов (Telegram tunnel или ingestion) требует пересборки, и я не хочу показывать нестабильный live. Лучше дать обзор контура и обсудить, что подключаем дальше.
```

---

## Что показывать в каждом tier

### T0 — full live (10–12 мин)

По `opus_result_next_demo_script.md`, 6 вопросов в порядке Q1→Q3→Q7→Q11→Q9→Q12. Включить greeting как 0-й шаг:

```
Шаг 0: «привет» → бот отвечает приветствием.
Шаг 1: Q1 испытательный срок ст. 70.
Шаг 2: Q3 договор поставки.
…
```

### T1 — live без greeting (8–10 мин)

Пропустить шаг 0. Перед шагом 1 устно проговорить: «Сейчас задаю содержательный вопрос — обработку приветствий обкатываем отдельно.»

```
Шаг 1: Q1 (открытие).
Шаг 2: Q3.
Шаг 3: Q7.
Шаг 4: Q11 (template draft).
Шаг 5: Q9 (refusal).
Шаг 6: Q12 (field_collection).
```

### T2 — PS only (6–8 мин)

Использовать `Invoke-Ask` функцию из `opus_result_next_presenter_checklist.md §UTF-8`. Открыть PS окно на screen-share, прогнать 4 ключевых вопроса:

```
1. $r = Invoke-Ask 'Сколько длится испытательный срок?'
   → показать $r | Select answer, confidence, sources

2. $r = Invoke-Ask 'Какие правила перевозки лития морскими судами?'
   → показать $r.refused = $true

3. $r = Invoke-Ask 'Подготовь черновик приказа о приёме: ФИО Иванов И.И., должность бухгалтер, дата 2026-06-01, оклад 80000, испытание 3 мес.'
   → показать draft + requires_human_review

4. $r = Invoke-Ask 'Подготовь приказ об увольнении.'
   → показать can_generate_draft=false + missing_fields
```

Сократить до 4 вопросов, чтобы экран PS не утомлял. Q3 и Q7 — резерв, если зритель просит ещё.

### T3 — только архитектура (5–7 мин)

```
1. README §Архитектура (Mermaid) — 1 мин: «Telegram → n8n → RAG API → Postgres/pgvector».
2. Swimlane diagram — 1 мин: «whitelist → классификация → hybrid retrieval → confidence policy → answer/refusal».
3. README §Current Status — 30 сек: documents=42, chunks=135, тесты 25 passed.
4. manifests/MANIFEST.md — 1 мин: «200 demo-документов, 7 категорий, source_type synthetic».
5. NORMATIVE_SOURCE_MANIFEST.md — 1 мин: «реальные нормативные акты с recommended_chunks».
6. opus_result_followup_answer_matrix.md — 1 мин: «вот как мы проверяем каждый ответ оффлайн».
7. Q&A по архитектуре.
```

---

## Минимальное приемлемое поведение Telegram (если T1)

Если оператор остался на T1, договоримся с Codex о минимальном hot-fix:

1. **`привет` НЕ должно вешать executions без ответа.** Допустимое поведение:
   - бот отвечает refusal text (что есть сейчас в /ask:570),
   - или бот отвечает «Здравствуйте» (если impl greeting_contract успел).
   - **НЕ допустимо:** silence.

2. **`/start` НЕ должно вызывать silence.** Допустимо: refusal text.

3. **Любой text → workflow execution создаётся.** Если execution не появляется — это уровнем выше (B1 tunnel или B3 workflow inactive); идти на T2.

4. **На любой ответ inline keyboard Good/Bad может отсутствовать.** Это лучше, чем silence.

Эти 4 условия — bare minimum для T1.

---

## Communication с Codex до T-0

Codex владеет fix. Operator обмен сообщениями с ним:

| Время | Operator | Codex |
|-------|----------|-------|
| T-60 мин | «Какой tier? Greeting fix готов?» | «T0/T1/T2 — обоснование» |
| T-30 мин | «Подтверди: `привет` отвечает текстом» | «yes/no + execution id» |
| T-15 мин | «Финальный go/no-go» | «T0 / T1» |
| T-5 мин | (свой smoke по чеклисту, не зависит от Codex) | (no ingestion / restart в окне) |
| T-0 | старт демо | passive monitoring |

Если Codex молчит к T-15 — operator идёт на T1 по умолчанию.

---

## Recovery в процессе демо

Если что-то ломается **во время** демо, не паниковать:

| Что сломалось | Реакция (вслух) | Tier downgrade |
|----------------|------------------|----------------|
| Telegram сообщение долго не приходит | «Сейчас покажу тот же запрос через API напрямую» → открыть PS | T1 → T2 |
| `/ask` вернул 5xx | «Перезапрашиваю» (один раз). Не помогло → следующий вопрос | пропустить вопрос |
| Refusal на content-вопросе (Q1 fail) | «Этот вопрос недоиндексировался, переключаюсь на резерв» → Q5 путевой лист | резерв |
| Internet/tunnel пропал | «Локальный API живой, покажу его» → PS | T2 |
| Полная заминка > 30 сек | «Подключение пересобирается, перейду к архитектуре» → слайды | T3 |

Главное правило: **не сидеть молча больше 15 секунд.** Любая заминка озвучивается и закрывается следующим шагом.

---

## Что НЕ делать во время демо

- Не открывать `.env` чтобы добавить ID зрителя — даже если очень просят.
- Не запускать `docker compose down` / `up --build` — гарантированный crash.
- Не показывать n8n executions с reply_markup raw JSON — там credentials могут промелькнуть.
- Не цитировать `getWebhookInfo` ответ — там TOKEN.
- Не обещать «починим за минуту» — лучше downgrade.

---

## После демо (debrief, 5 мин)

1. Какой tier фактически шёл (T0/T1/T2/T3)?
2. Что зрители заметили (вопросы, недоумения)?
3. Что упало во время демо и почему — добавить в `opus_result_followup_risk_burndown.md` как post-incident risk?
4. Решение по greeting fix: оставлять на n8n стороне или переносить классификатор в Python?

Эти 4 пункта — короткий лог в отдельный файл `opus_result_followup_demo_postmortem.md` (если operator его попросит).

## Verification (self-check)

- 4 tier'а демо (T0/T1/T2/T3) с чёткими условиями входа и контентом.
- 16 go/no-go checkpoint'ов привязаны к временной шкале T-10 → T-0.
- Decision matrix tier'а на T-1 — четыре строки, четыре исхода.
- Wording для каждого tier'а готовый — operator не сочиняет на ходу.
- Recovery таблица в процессе демо — что говорить и куда переключаться.
- Минимальное приемлемое Telegram (T1) — 4 условия, проверяемые offline.
- Communication с Codex — 5 точек.
- Проектные файлы не редактировались.
