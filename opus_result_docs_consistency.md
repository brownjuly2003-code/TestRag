# Opus Result: Documentation Consistency Review

> Files reviewed: `README.md`, `docs/demo-runbook.md`, `docs/next-session.md`, `mvp-plan.md`.
> Method: read all four files in full, cross-check claims about status, paths, env-keys, terminology, structure. No edits performed; this report only lists findings + suggested wording.
> Severity legend: **HIGH** — может ввести пользователя/демо-зрителя в заблуждение или сломать setup; **MEDIUM** — устаревшая информация без блокировки; **LOW** — косметика.

## Findings

### 1. README §«Текущий статус реализации» (lines 125–133) — устарел [HIGH]

**Текущее:** «Добавлен RAG API на FastAPI… Добавлены стартовые демо-документы.» Не отражает, что в Postgres уже есть ingestion, n8n workflow активирован, whitelist настроен, тесты `11 passed`.

**Действующая правда (из `mvp-plan.md` §Current Status, updated 2026-05-16):** Docker Compose поднят, workflow активирован, локальный Telegram whitelist настроен для `432751211`, `/health` возвращает `postgres_enabled=true`, `mistral_enabled=true`, `embeddings_enabled=true`, `documents=4`, `document_chunks=4`, `request_logs=11`, тесты `python -m pytest -p no:schemathesis` → `11 passed`.

**Предлагаемая правка README §125–133:**

```markdown
## Текущий статус реализации

Updated: 2026-05-16 (см. также `mvp-plan.md`).

- Docker Compose поднят: `postgres`, `rag-api`, `n8n`.
- RAG API: FastAPI + Mistral + Postgres/pgvector. `/health` возвращает `postgres_enabled`, `mistral_enabled`, `embeddings_enabled` = `true`.
- BM25 retriever и policy отказа при низкой уверенности активны.
- В Postgres: документы, чанки, логи, feedback, очередь ревью созданы; в текущем срезе `documents=4`, `document_chunks=4` (минимальный sample, до отбора MVP-корпуса из `corpus/`).
- n8n workflow `hr-legal-rag-workflow.json` импортирован и активирован.
- Локальный Telegram whitelist настроен.
- Тесты: `python -m pytest -p no:schemathesis` → 11 passed.
- Mistral подключается через env. Если `MISTRAL_API_KEY` пустой, API возвращает grounded extractive answer по найденным источникам.
```

---

### 2. Терминология Supabase vs Postgres/pgvector — несогласована [HIGH]

`mvp-plan.md §Notes` уже фиксирует это как открытый пункт:
> «Синхронизировать документацию по терминам Postgres/pgvector и Supabase.»

**Конкретные места:**

| Файл | Строки | Текущая фраза | Несогласованность |
|---|---|---|---|
| `README.md` | 18 («хранение чанков и embeddings в Supabase `pgvector`») | Supabase | Локально используется Postgres из Docker Compose |
| `README.md` | 24 («Supabase pgvector») | Supabase | то же |
| `README.md` | 45 («Supabase \| pgvector, документы, чанки…») | Supabase | то же |
| `README.md` | 137–155 (Mermaid architecture: `Supabase[(Supabase pgvector)]`, `Logs[(Supabase logs)]`) | Supabase | то же |
| `README.md` | 213–214 («хранение в Supabase pgvector») | Supabase | то же |
| `README.md` | 222 («BM25 в RAG API… Supabase при этом остается источником текстов») | Supabase | то же |
| `README.md` | 257–270 §Конфигурация: `SUPABASE_URL=`, `SUPABASE_SERVICE_ROLE_KEY=` | требует Supabase env | В Docker Compose эти переменные не используются |

**Предлагаемая правка:** ввести явный disclaimer в верхней части README:

```markdown
> Архитектура MVP: локально используется Postgres 16 + pgvector через `docker-compose.yml`. Supabase упоминается как возможный production target, но для self-hosted demo не обязателен. Env-блок ниже описывает обе конфигурации; для локального запуска `SUPABASE_*` переменные не нужны.
```

И в §Конфигурация явно отделить «локальные обязательные» от «production-only»:

```env
# Локальный MVP (docker-compose)
TELEGRAM_BOT_TOKEN=
ALLOWED_TELEGRAM_USER_IDS=
MISTRAL_API_KEY=                    # опционально, иначе extractive answer

# Production (опционально)
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
N8N_WEBHOOK_URL=                    # для live Telegram через tunnel
N8N_WEBHOOK_SECRET=
```

---

### 3. README §«Структура проекта» (lines 106–117) — устарела [MEDIUM]

**Текущее:** перечислены только `docker-compose.yml`, `sql/init.sql`, `data/sample_docs/`, `docs/`, `n8n/`, `rag-api/`.

**Не упомянуто (реально присутствует в `D:\TestRag\`):**
- `corpus/` — 196+ markdown-файлов
- `manifests/MANIFEST.md`, `manifests/NORMATIVE_SOURCE_MANIFEST.md` — основа отбора и нормативной обвязки
- `normative/` — пустая, но зарезервирована
- `prompts/GENERATE_BATCH_1.md`
- `pytest.ini`
- `opus_task.md` (текущая Opus-сессия)

**Предлагаемая правка §Структура проекта:**

```text
TestRag/
  docker-compose.yml
  sql/init.sql
  data/sample_docs/
  corpus/                                       # full corpus 200 docs, см. manifests
  manifests/MANIFEST.md                         # реестр демо-документов с frontmatter
  manifests/NORMATIVE_SOURCE_MANIFEST.md        # реестр нормативных источников (ТК, ГК, ФЗ)
  normative/                                    # зарезервировано для нормативных текстов
  prompts/                                      # промпты пакетной генерации
  docs/demo-runbook.md
  docs/legal-document-prompts.md
  docs/next-session.md
  n8n/workflows/hr-legal-rag-workflow.json
  rag-api/app/
  rag-api/tests/
  pytest.ini
```

---

### 4. `docs/next-session.md` — устаревший статус [HIGH]

**Места:**
- Line 25: «pytest: 3 теста проходили» — на 2026-05-16 уже `11 passed`.
- Lines 22, 30: «sample docs в data/sample_docs», «Подключить ingestion в Postgres: chunks + Mistral embeddings + document_chunks.» — этот пункт уже **[x]** в `mvp-plan.md`.
- Line 31: «Подключить реальные логи request_logs, answer_feedback, review_queue.» — уже **[x]** (`request_logs=11`, `answer_feedback=1`, `review_queue=1`).
- Line 32: «Добавить endpoint для document draft/type detection по docs/legal-document-prompts.md.» — частично закрыт в mvp-plan `[x] Добавить генерацию черновика по 1 шаблону`.
- Line 28: «Что уже сделано:» — список нужно подравнять под `mvp-plan.md §Current Status`.

**Предлагаемая правка `docs/next-session.md`:** заменить разделы «Что уже сделано» и «Что нужно делать дальше» на ссылку: `См. mvp-plan.md (Current Status + Next Tasks).` Чтобы не дублировать факт-статус в двух файлах — единый источник истины это `mvp-plan.md`.

Минимальный pattern для next-session.md:

```markdown
# Next Session

## Как начать следующую сессию

Скопируй в новый чат:

```text
Продолжаем проект D:\TestRag.

Контекст и текущий статус — в mvp-plan.md (Current Status + Next Tasks).
Архитектура и быстрый запуск — в README.md.
Demo flow — в docs/demo-runbook.md.

Перед работой:
- Не выводить .env и секреты.
- После изменений: python -m pytest -p no:schemathesis.
- Если трогаешь Docker, проверять docker compose config --quiet.
```
```

---

### 5. `docs/demo-runbook.md` line 11 — «при наличии MISTRAL_API_KEY» [LOW]

Корректно (API даёт extractive fallback), но не показывает читателю, **что меняется**: если ключа нет → нет векторных embeddings → BM25-only retrieval → ниже recall. Это нужно явно отметить, иначе на демо без ключа `confidence` будет хронически низкий, а оператор не поймёт, что сделал не так.

**Предлагаемая правка демо-runbook §Подготовка п.3:**

```markdown
3. Заполнить `TELEGRAM_BOT_TOKEN`, `ALLOWED_TELEGRAM_USER_IDS` и `MISTRAL_API_KEY`.
   Без `MISTRAL_API_KEY` сервис работает в режиме extractive-only (BM25 без векторов), confidence по тем же вопросам будет ниже, а часть демо-кейсов получит refusal вместо ответа.
```

---

### 6. `docs/demo-runbook.md` lines 64–71 — cloudflared docker, network name [MEDIUM]

```
docker run -d --name testrag-cloudflared --network testrag_default cloudflare/cloudflared:latest tunnel --no-autoupdate --url http://n8n:5678
```

Имя сети `testrag_default` зависит от того, как Docker Compose нормализует project-name. На Windows с `docker compose v2` projectname = имя папки в нижнем регистре без подчёркиваний → `testrag-default`, а не `testrag_default`. Если у пользователя `compose.project-name` не переопределён, команда упадёт `network testrag_default not found`.

**Предлагаемая правка:** перед `docker run` добавить шаг:

```powershell
docker network ls --filter "name=testrag" --format '{{.Name}}'
```

И в команде использовать переменную/найденное имя, например пометить: `--network <имя_сети_из_docker_network_ls>`.

---

### 7. `mvp-plan.md` §Current Status `documents=4, document_chunks=4` vs `corpus/` 196 файлов [MEDIUM]

Состояние совместимое (Next Tasks явно требует «Подключить выбранный корпус к ingestion вместо минимального `data/sample_docs`»). Но: README обещает в §MVP «индексация 3-50 открытых документов» — текущее значение 4 формально внутри коридора, но фактически минимальный sample, не shortlist. Для демо это **ниже порога reliability** на reasonable HR/legal вопросы.

**Предлагаемая правка `mvp-plan.md §Current Status`:** добавить строку:
```markdown
- [ ] MVP corpus shortlist (`corpus/` → ingestion) **не подключен**, в базе только sample 4 чанка — большинство нормативных вопросов попадут в refusal до завершения этого таска.
```

---

### 8. README §«Документация» (lines 119–123) — нет ссылки на manifests, mvp-plan [MEDIUM]

В списке только три doc-файла. Не упомянуты:
- `mvp-plan.md` (фактический живой статус)
- `manifests/MANIFEST.md` (200 демо-документов)
- `manifests/NORMATIVE_SOURCE_MANIFEST.md` (нормативные источники)

**Предлагаемая правка §Документация:**

```markdown
- [MVP Plan](mvp-plan.md) - живой статус MVP, current state, next tasks, done-when.
- [Manifest корпуса](manifests/MANIFEST.md) - 200 демо-документов: doc_id, тип, департамент, приоритет.
- [Manifest нормативных источников](manifests/NORMATIVE_SOURCE_MANIFEST.md) - ТК, ГК, ФЗ с recommended_chunks.
- [Demo Runbook](docs/demo-runbook.md) - как показать локальное демо.
- [Legal Document Prompts](docs/legal-document-prompts.md) - prompt для классификации юр/HR-документов.
- [Next Session](docs/next-session.md) - стартовый prompt для новой сессии Claude.
```

---

### 9. README §Архитектура (Mermaid) (lines 137–155) — `Supabase pgvector`, `Supabase logs` [MEDIUM]

Связано с §2. Диаграмма показывает Supabase, но в Docker Compose работает локальный Postgres.

**Предлагаемая правка:** заменить `Supabase[(Supabase pgvector)]` → `Postgres[(Postgres + pgvector)]`, `Logs[(Supabase logs)]` → `Logs[(Postgres: request_logs / feedback / review_queue)]`. Если важна Supabase как production target, отрисовать одну диаграмму для локального MVP, вторую — для возможного prod (или оставить один заголовок «Production target: Supabase»).

---

### 10. README §«Быстрый запуск» — нет пункта про `docker compose config --quiet` и `python -m pytest` [LOW]

`docs/next-session.md` §Минимальные команды и `mvp-plan.md` упоминают эти проверки. README в Quickstart их нет.

**Предлагаемая правка README §Быстрый запуск, после п.5:**

```markdown
6. Проверить, что compose-конфиг и тесты валидны (минимальная sanity-проверка перед демо):

```powershell
docker compose config --quiet
python -m pytest -p no:schemathesis
```
```

---

### 11. README §«Вопросы к заказчику» (lines 301–309) — потенциально дублируется с `mvp-plan.md` [LOW]

Эти вопросы повторяют темы, частично решённые: «Где должны храниться логи: Supabase или Google Sheets?» — фактически логи уже в Postgres. Можно либо помечать «закрыто» внутри списка, либо перенести только открытые в `mvp-plan.md §Notes`.

**Предлагаемая правка:** добавить столбец «статус» к списку, например:

```markdown
- Какие типы документов и вопросов приоритетны для демо? **открыто**
- Какие источники считать допустимыми для юридических ссылок? **частично закрыто — NORMATIVE_SOURCE_MANIFEST.md**
- Где должны храниться логи: Supabase или Google Sheets? **закрыто — Postgres**
- Кто будет ревьюить плохие ответы и с какой периодичностью? **открыто**
```

---

### 12. `docs/demo-runbook.md` lines 23–42 §«Импорт n8n Через CLI» — рассогласовано с `mvp-plan.md` [LOW]

`mvp-plan.md`: «n8n workflow активирован, публичный webhook отвечает без ошибок». То есть для текущего deployment эти команды CLI не нужны. Они актуальны только для повторной/чистой переустановки.

**Предлагаемая правка:** добавить в начало §«Импорт n8n Через CLI» аннотацию:

```markdown
> Этот раздел нужен только при первой установке или после `docker compose down -v`. Если `n8n.workflow_entity` уже содержит активный `testrag-hr-legal-assistant` (это так в текущем deployment, см. mvp-plan.md §Current Status), пропустите шаг.
```

---

## Сводная таблица severity

| # | Файл | Раздел/строки | Severity |
|---|------|---------------|----------|
| 1 | README.md | §Текущий статус 125–133 | HIGH |
| 2 | README.md, all | терминология Supabase vs Postgres | HIGH |
| 3 | README.md | §Структура 106–117 | MEDIUM |
| 4 | docs/next-session.md | Что сделано/Что дальше | HIGH |
| 5 | docs/demo-runbook.md | §Подготовка п.3 | LOW |
| 6 | docs/demo-runbook.md | cloudflared network 64–71 | MEDIUM |
| 7 | mvp-plan.md | §Current Status corpus state | MEDIUM |
| 8 | README.md | §Документация 119–123 | MEDIUM |
| 9 | README.md | §Архитектура Mermaid | MEDIUM |
| 10 | README.md | §Быстрый запуск | LOW |
| 11 | README.md | §Вопросы к заказчику | LOW |
| 12 | docs/demo-runbook.md | §Импорт n8n CLI 23–42 | LOW |

## Что НЕ затронуто (выглядит консистентно)

- README §RAG-логика (lines 234–246) — соответствует actual flow в `rag-api/app/`.
- README §Безопасность (lines 272–279) — соответствует `legal-document-prompts.md`.
- demo-runbook §«Проверка отказа» (lines 102–111) — вопрос «литий морем» корректен и совпадает с demo question #9 из `opus_result_demo_questions.md`.
- `mvp-plan.md §Done When` — отражает реальный gap (Telegram live path не подтверждён).

## Никаких правок в файлах не сделано

Все изменения предложены текстом, чтобы Codex мог интегрировать без merge-конфликтов в текущую работу.
