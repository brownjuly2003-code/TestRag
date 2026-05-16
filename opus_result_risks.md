# Opus Result: Demo Risk Review

> Source data: `README.md`, `docs/demo-runbook.md`, `docs/next-session.md`, `mvp-plan.md`, `manifests/MANIFEST.md`, `manifests/NORMATIVE_SOURCE_MANIFEST.md`, `docs/legal-document-prompts.md`.
> Scope: риски, видимые в документации/манифестах без чтения кода `rag-api/` или импорта workflow.
> Шкала: Likelihood = вероятность инцидента на демо (1–5), Impact = ущерб демо/доверию заказчика (1–5). Score = L × I, sort desc.

## Top risks (ranked)

### R1. Stale tunnel URL / Telegram webhook не доставится [Score 25 = L5×I5]

**Сценарий.** `docs/demo-runbook.md §«Локальный Telegram Webhook»` использует `cloudflared --url http://n8n:5678`. trycloudflare-URL **меняется при каждом запуске контейнера** и не персистентен. `mvp-plan.md §Done When` отдельно отмечает, что Telegram live path не подтверждён. Если за час до демо контейнер `testrag-cloudflared` был перезапущен (Docker Desktop reboot, ноут спал, network change) — URL умер.

**Likelihood = 5:** trycloudflare умирает при любом docker restart и доступности сети; на демо-нагрузке часто.
**Impact = 5:** ломает весь Telegram-сценарий, который заявлен как главный flow.

**Мitigation (до демо, 5–10 минут):**
1. Проверить `docker logs testrag-cloudflared` за последние 30 мин — нет ли реконнектов.
2. Перед демо вручную пересоздать tunnel **за час**, не за 5 минут.
3. Записать актуальный URL в `.env` И в Telegram BotFather (`setWebhook`) И force-recreate `n8n` — иначе bot будет писать в старый URL.
4. План Б: иметь готовый «локальный» сценарий (PowerShell `Invoke-RestMethod` на `:8000/ask`) — показывать архитектуру без Telegram, если tunnel умер.

---

### R2. Missing whitelist / `ALLOWED_TELEGRAM_USER_IDS` пуст или содержит чужой ID [Score 16 = L4×I4]

**Сценарий.** `docs/demo-runbook.md §«Whitelist Telegram»`: «Пустой `ALLOWED_TELEGRAM_USER_IDS` не открывает доступ всем. Бот ответит пользователю его Telegram ID». `mvp-plan.md §Current Status`: настроен для `432751211`. Если демо ведёт другой человек со своего аккаунта или один из зрителей пишет боту — он получит «вы не в whitelist», и это интерпретируется как «бот не работает».

**Likelihood = 4:** для демо часто хочется показать «вживую с зрителем»; добавить ID одним движением — забывается.
**Impact = 4:** сценарий read-only становится неубедительным, особенно если зритель сам пишет.

**Мitigation:**
1. До демо явно проговорить: «писать буду только я с аккаунта 432751211». ID не разглашать.
2. Если зритель хочет «сам попробовать» — подготовить заранее: добавить его ID в `.env`, `docker compose up -d --force-recreate n8n`, дождаться 30 секунд.
3. Не открывать `.env` на share-экране при добавлении ID.

---

### R3. Low source coverage (4 чанка) — большинство вопросов получит refusal [Score 16 = L4×I4]

**Сценарий.** `mvp-plan.md §Current Status`: `documents=4, document_chunks=4`. MVP-корпус из `corpus/` (200 файлов) **ещё не подключён** (явно в Next Tasks). Большинство демо-вопросов из `opus_result_demo_questions.md` (особенно #5 путевой лист, #6 CMR, #7 ПДн, #8 коммерческая тайна, #11/12 черновики) попадут в refusal или MEDIUM confidence, потому что у retrieval банально нет фактуры.

**Likelihood = 4:** на 4 чанках только ст.70 ТК есть с гарантией.
**Impact = 4:** demo выглядит как «бот всё время отказывается отвечать», тогда как это **не safety**, а **пустой индекс**.

**Мitigation:**
1. До демо либо подключить shortlist (см. `opus_result_corpus.md`), либо явно проговорить: «индекс минимальный, полный набор — следующий таск».
2. Из 12 вопросов в `opus_result_demo_questions.md` выбрать только те, которые покрыты текущим sample (вероятно #1, #9 refusal — единственные стабильные).
3. Согласовать с Codex: до демо ingestion shortlist — top-priority следующая итерация.

---

### R4. Synthetic-only corpus принят за реальные регламенты [Score 12 = L3×I4]

**Сценарий.** `manifests/MANIFEST.md §header`: «все документы с `source_type: synthetic_internal` созданы исключительно для демонстрационного корпуса и требуют замены на реальные документы заказчика». Если на демо зрителю не подсветить, что политики/регламенты в индексе synthetic — он может процитировать их потом «как наш регламент» и это создаст compliance-проблему.

**Likelihood = 3:** если есть legal-аудитория, риск выше; demo-оператор может забыть.
**Impact = 4:** репутационный / compliance.

**Мitigation:**
1. Перед каждым ответом, который опирается на корпусные документы, упомянуть «это demo-content, в production будет ваш регламент».
2. В UI/ответе RAG API желательно добавить badge `[demo-synthetic]` для документов с `source_type: synthetic_internal` — это идёт за рамки «no-code» задач Opus, передать Codex.
3. На презентации иметь slide-disclaimer «корпус — синтетический, нормативные ссылки — реальные».

---

### R5. Encoding (UTF-8 / Windows / PowerShell) поломает кириллицу в выводе [Score 12 = L3×I4]

**Сценарий.** `docs/next-session.md §Минимальные команды` — PowerShell. `docs/demo-runbook.md` использует `Invoke-RestMethod -Body '{"question":"Что говорит статья 70…"}'`. На PowerShell 5.1 (Windows 10/11 default) кодировка по умолчанию для `-Body` строки в JSON может быть Windows-1251 при `Invoke-RestMethod`. Если сервер не указывает `Content-Type: application/json; charset=utf-8` явно, вопрос превратится в `Что говорит сÑ‚Ð°Ñ‚ÑŒÑŽ`, embeddings будут мусором, retrieval вернёт пусто, демо-вопрос #1 (главный) даст refusal.

**Likelihood = 3:** на чистом PowerShell 5.1 — реально; на 7.x с UTF-8 default — нет.
**Impact = 4:** легитимный happy-path ломается, выглядит как fail модели.

**Memory pin:** `~/.claude/memory/feedback_windows_cp1252_pipe.md` — Юлия знает эту проблему отдельно (codex TUI cyrillic). Cm здесь тот же класс.

**Мitigation:**
1. До демо проверить `$PSVersionTable.PSVersion` — если 5.1, в Body передавать byte-encoded UTF-8:
   ```powershell
   $bodyBytes = [System.Text.Encoding]::UTF8.GetBytes('{"question":"Что говорит статья 70 ТК РФ про испытание?"}')
   Invoke-RestMethod -Method Post -Uri 'http://localhost:8000/ask' -ContentType 'application/json; charset=utf-8' -Body $bodyBytes
   ```
2. Альтернатива — использовать Windows Terminal с PowerShell 7 и `chcp 65001` заранее.
3. Запустить Smoke step 5 из `opus_result_checklist.md` за **15 минут** до демо и визуально проверить, что в `answer` кириллица читаемая.

---

### R6. Legal disclaimer gap в ответах [Score 12 = L3×I4]

**Сценарий.** `docs/legal-document-prompts.md` чётко указывает: «Не давай юридическую гарантию корректности», «черновик должен явно содержать пометку "Требует проверки юристом/HR"». Если фактический endpoint `/ask` или его рендеринг в Telegram **не добавляет** этот disclaimer (особенно для intent=template_draft), зритель может расценить ответ как «совет юриста».

**Likelihood = 3:** код endpoint не читали (Opus scope), но в текущем минимальном sample вопрос-черновик неактивен (R3).
**Impact = 4:** safety-фейл; для legal-аудитории — критично.

**Мitigation:**
1. Шаг 15 чеклиста проверяет `requires_human_review = true` на template_draft.
2. Перед демо вручную прогнать вопрос #11 из `opus_result_demo_questions.md` — убедиться, что в `answer` или `disclaimer` поле есть «Требует проверки юристом/HR».
3. Если отсутствует — попросить Codex добавить **до** демо (это уже выходит из Opus scope no-code).

---

### R7. trycloudflare URL логируется в чистом виде / показывается на share-экране [Score 9 = L3×I3]

**Сценарий.** `docs/demo-runbook.md` командует `docker logs testrag-cloudflared` — URL виден в логе. Если демо-оператор перед началом screen-share открывает терминал и пробегает по логам — публичный URL попадает в запись/трансляцию. Сам по себе trycloudflare URL не критичен, но если он раскрывает internal маппинг и зрители могут начать слать туда payloads — n8n с whitelist выдержит, но request_logs замусорятся.

**Likelihood = 3:** при screen-share регулярно открывают терминал.
**Impact = 3:** низкий ущерб, но «грязный» демо-логи.

**Мitigation:**
1. Закрыть терминал с логами до share-экрана.
2. После демо `docker rm -f testrag-cloudflared` (но это меняет инфру — согласовать с Codex; в нашей задаче только flag).

---

### R8. Refusal сообщение слишком резкое и звучит как «бот не работает» [Score 8 = L4×I2]

**Сценарий.** `docs/demo-runbook.md §«Проверка отказа»`: «ответ сообщает, что источников недостаточно». Если текст refusal слишком сухой («недостаточно источников»), зритель воспринимает это не как safety, а как «не нашло».

**Likelihood = 4:** на 4-чанковом sample refusal будет случаться часто.
**Impact = 2:** только восприятие, не функциональный fail.

**Мitigation:**
1. До демо проверить exact wording в `answer` на refusal-запросе.
2. Если фраза скудная — Codex может усилить: «По заданному вопросу в проиндексированной базе недостаточно нормативных источников. Уточните формулировку или укажите номер документа/статьи.» Это вне Opus scope, но фиксируем.

---

### R9. `request_logs` не записывает на refusal → демо «без логов» [Score 8 = L2×I4]

**Сценарий.** `mvp-plan.md §Done When` отмечает «Все запросы и оценки логируются» как `[x]`. Но если refusal-flow обходит логирование (раннее return до записи), на демо счётчик логов не увеличится → шаг 11 чеклиста покажет, что после трёх вопросов «logs не растут».

**Likelihood = 2:** в коде Opus не читал; обычно RAG API логирует ВСЕ запросы, включая refusal.
**Impact = 4:** ломает шаг 11 чеклиста.

**Мitigation:**
1. Шаг 11 чеклиста выполнить **до** и **после** smoke-вопросов: убедиться, что delta = 2 (или 3, в зависимости от того, попадают ли refusal в логи).
2. Если refusal не логируется — это design choice, можно проговорить «refusal сам по себе не несёт risk для аналитики».

---

### R10. Документация противоречит сама себе (Supabase vs Postgres) [Score 6 = L3×I2]

**Сценарий.** `opus_result_docs_consistency.md` findings #2, #9: README показывает Supabase, Compose использует локальный Postgres. Если на демо зритель посмотрит README на GitHub и спросит «а Supabase у вас есть?», ответ потребует пояснений.

**Likelihood = 3:** только если зритель полез в README.
**Impact = 2:** разъяснение, не блокер.

**Мitigation:**
1. Не открывать README на share-экране. Использовать `mvp-plan.md` как презентационный документ.
2. Долгосрочно — фиксить (см. `opus_result_docs_consistency.md` #2).

---

### R11. Бесконтрольные `corpus/` edits во время демо [Score 4 = L2×I2]

**Сценарий.** В `opus_task.md` явно запрещено трогать `corpus/*.md`, потому что там может идти параллельная работа Codex. Если Codex во время демо запускает ingestion / re-index, индекс может «дёрнуться» в момент демо-вопроса.

**Likelihood = 2:** требует одновременной работы Codex.
**Impact = 2:** один странный ответ.

**Мitigation:**
1. До демо синхронизироваться с Codex: «не запускай ingestion в окно T-15 → T+30 мин от демо».

---

### R12. `MANIFEST.md` 8170 строк не открывается в `Read` стандартно (>256KB) [Score 3 = L3×I1]

**Сценарий.** Если демо-оператор захочет «показать MANIFEST зрителю», открыть его в VS Code/Notepad может занять секунды.

**Likelihood = 3:** редко.
**Impact = 1:** косметика.

**Мitigation:** на этом focal-point демо не показывать MANIFEST live; иметь подготовленный shortlist (`opus_result_corpus.md`).

---

## Сводный rank

| Rank | Risk | L | I | Score | Mitigation owner |
|------|------|---|---|-------|------------------|
| 1 | Stale tunnel URL | 5 | 5 | 25 | Demo operator + Codex |
| 2 | Missing whitelist | 4 | 4 | 16 | Demo operator |
| 3 | Low source coverage | 4 | 4 | 16 | Codex (ingestion) |
| 4 | Synthetic corpus mistaken for real | 3 | 4 | 12 | Demo operator (verbal) + Codex (badge) |
| 5 | PowerShell UTF-8 encoding | 3 | 4 | 12 | Demo operator |
| 6 | Legal disclaimer gap | 3 | 4 | 12 | Codex (verify endpoint) |
| 7 | trycloudflare URL leaks via screen-share | 3 | 3 | 9 | Demo operator |
| 8 | Refusal wording sounds like fail | 4 | 2 | 8 | Codex |
| 9 | Refusal не пишет в `request_logs` | 2 | 4 | 8 | Codex (verify) |
| 10 | Supabase vs Postgres docs mismatch | 3 | 2 | 6 | Codex (docs fix) |
| 11 | Bесконтрольные corpus-edits во время демо | 2 | 2 | 4 | Codex (coordination) |
| 12 | MANIFEST 8170 строк | 3 | 1 | 3 | Demo operator |

## Резюме критических 5

1. Tunnel URL — перепроверить за час до демо.
2. Whitelist — не открывать `.env` на экране, проверить, что нужный ID в списке.
3. Source coverage — либо подключить shortlist, либо явно proговорить «sample».
4. Synthetic-content disclaimer — каждое цитирование маркировать «demo».
5. PowerShell UTF-8 — на PS 5.1 использовать `[Encoding]::UTF8.GetBytes(...)` или перейти на PS 7 + chcp 65001.

## Что НЕ покрыто этим обзором

- Уязвимости кода `rag-api/app/` (вне Opus scope: запрещено читать).
- Безопасность n8n credentials (только envs, не open-able).
- Performance / latency на 10+ одновременных запросах (требует нагрузочного теста).
- Точность retrieval на полном corpus (требует прогона, не возможен без ingestion).
- Privacy / GDPR-аспекты Telegram-бота (запрет на live testing).
