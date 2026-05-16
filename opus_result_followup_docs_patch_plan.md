# Opus Result Followup: Docs Patch Plan

> Источник: `opus_result_next_docs_delta.md` (9 ещё-открытых пунктов + 3 новых после Codex-pass).
> Назначение: ready-to-apply patch-set для Codex. Не редактирую файлы сама — даю target + section + proposed wording.
> Порядок: HIGH → MEDIUM → LOW. Внутри уровня — по minimal blast radius.
> Никакие проектные файлы не редактировались.

## Сводный приоритезированный список

| # | Target | Section | Priority | Тип патча |
|---|--------|---------|----------|-----------|
| P1 | `README.md` | §Конфигурация (lines ~272–287) | **HIGH** | Cleanup |
| P2 | `README.md` | §Текущий статус (lines ~136–148) | **HIGH** | Update facts |
| P3 | `README.md` | §Документация (lines ~130–134) | MEDIUM | Add links |
| P4 | `README.md` | §Структура проекта (lines ~113–128) | MEDIUM | Expand tree |
| P5 | `docs/demo-runbook.md` | §Локальный Telegram Webhook (lines ~83–90) | MEDIUM | Add network-detect step |
| P6 | `README.md` | §Быстрый запуск (lines ~76–111) | LOW | Add sanity step |
| P7 | `README.md` | §Вопросы к заказчику (lines ~318–327) | LOW | Add status markers |
| P8 | `docs/demo-runbook.md` | §Подготовка (line ~11) | LOW | Wording precision |
| P9 | `docs/demo-runbook.md` | §Импорт n8n Через CLI (lines ~42–61) | LOW | Add annotation |
| P10 | `README.md` | §Конфигурация .env block (lines ~284–286) | LOW | Default flip |
| P11 | `mvp-plan.md` | §Next Tasks (line ~37) | LOW | Add owner |

---

## P1 — README §Конфигурация: убрать SUPABASE_* или явно отделить [HIGH]

**Target:** `README.md` §Конфигурация, блок ```env ...``` (примерно lines 274–287).

**Why HIGH:** docker-compose не использует SUPABASE_*, но README в обязательных env. Setup-разработчик будет искать creds, которых нет в проекте.

**Current text (для замены):**
```env
TELEGRAM_BOT_TOKEN=
MISTRAL_API_KEY=
MISTRAL_CHAT_MODEL=
MISTRAL_EMBEDDING_MODEL=
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
N8N_WEBHOOK_SECRET=
ALLOWED_TELEGRAM_USER_IDS=
DOCS_PATH=/app/data/sample_docs
DOCS_MANIFEST_PATH=
```

**Proposed text:**
```env
# Локальный MVP (docker-compose)
TELEGRAM_BOT_TOKEN=
ALLOWED_TELEGRAM_USER_IDS=
MISTRAL_API_KEY=
MISTRAL_CHAT_MODEL=
MISTRAL_EMBEDDING_MODEL=
N8N_WEBHOOK_SECRET=
N8N_WEBHOOK_URL=                                       # для live Telegram через HTTPS tunnel
DOCS_PATH=/app/corpus                                  # default для MVP-корпуса
DOCS_MANIFEST_PATH=/app/manifests/MVP_CORPUS_FILES.txt # ограничивает индексацию выбранными файлами

# Production target (не используется в локальном docker-compose)
# SUPABASE_URL=
# SUPABASE_SERVICE_ROLE_KEY=
```

**Также:** добавить одну строку перед блоком:
```markdown
Локальный setup использует только верхний блок переменных. Supabase указан как опциональный production target — закомментирован, чтобы не путать setup.
```

**Rationale:** одним блоком закрываем и оставшуюся часть finding #2 (Supabase mismatch), и N1 (default DOCS_PATH). После патча setup-разработчик скопирует только живой набор.

---

## P2 — README §Текущий статус: подтянуть факты до mvp-plan [HIGH]

**Target:** `README.md` §Текущий статус реализации (lines 136–148).

**Why HIGH:** README — первое, что читает рекрутёр/заказчик. Сейчас он отстаёт от `mvp-plan.md §Current Status` по двум пунктам: реальный chunk_count и факт активации workflow.

**Proposed addition (вставить после строки «- Mistral подключается через env...»):**
```markdown
- В Postgres проиндексирован MVP-корпус: `documents=42`, `document_chunks=122` (см. `mvp-plan.md §Current Status`).
- n8n workflow `hr-legal-rag-workflow.json` импортирован и активирован.
- Telegram whitelist настроен в `.env` (`ALLOWED_TELEGRAM_USER_IDS`).
```

**Rationale:** одним блоком из 3 строк закрываем README §статус vs mvp-plan §Current Status. Числа поддерживать вручную (или Codex может добавить badge с автоупдейтом из `/health`).

---

## P3 — README §Документация: добавить mvp-plan и manifests [MEDIUM]

**Target:** `README.md` §Документация (lines 130–134).

**Proposed text (замена всего раздела):**
```markdown
## Документация

- [MVP Plan](mvp-plan.md) — живой статус MVP: current state, next tasks, done-when.
- [Demo Runbook](docs/demo-runbook.md) — как показать локальное демо.
- [Legal Document Prompts](docs/legal-document-prompts.md) — большой prompt для определения типа юр/HR-документа и безопасной подготовки черновика.
- [Next Session](docs/next-session.md) — стартовый prompt для новой сессии Claude.
- [Manifest корпуса](manifests/MANIFEST.md) — 200 демо-документов: doc_id, тип, департамент, приоритет, `source_type`.
- [Манифест нормативных источников](manifests/NORMATIVE_SOURCE_MANIFEST.md) — реестр ТК, ГК, ФЗ, приказов с `recommended_chunks`.
- [MVP corpus shortlist](manifests/MVP_CORPUS_FILES.txt) — список файлов из `corpus/`, реально подающихся на индексацию.
```

**Rationale:** превращает README в полноценную точку входа без хождения через каталоги. Закрывает finding #8.

---

## P4 — README §Структура проекта: дополнить дерево [MEDIUM]

**Target:** `README.md` §Структура проекта (lines 113–128).

**Proposed text:**
```text
TestRag/
  docker-compose.yml
  mvp-plan.md
  sql/init.sql
  data/sample_docs/
  corpus/                                       # full corpus ~200 docs
  manifests/MANIFEST.md                         # реестр демо-документов с frontmatter
  manifests/MVP_CORPUS_FILES.txt                # список файлов, реально подающихся на индексацию
  manifests/NORMATIVE_SOURCE_MANIFEST.md        # реестр ТК, ГК, ФЗ, приказов
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

**Rationale:** закрывает finding #3 PARTIAL. Совпадает с фактической структурой `D:\TestRag\`.

---

## P5 — demo-runbook §Локальный Telegram Webhook: cloudflared network [MEDIUM]

**Target:** `docs/demo-runbook.md` §Локальный Telegram Webhook (lines 83–90).

**Current text:**
```powershell
docker run -d --name testrag-cloudflared --network testrag_default cloudflare/cloudflared:latest tunnel --no-autoupdate --url http://n8n:5678
docker logs testrag-cloudflared
```

**Proposed text:**
```powershell
# 1. Определить точное имя docker-сети — Compose v2 нормализует project-name по-разному
#    на Windows / Linux. Имя сети может быть testrag_default или testrag-default.
docker network ls --filter "name=testrag" --format '{{.Name}}'

# 2. Запустить cloudflared, подставив имя из вывода (пример: testrag_default).
docker run -d --name testrag-cloudflared `
    --network <network_name> `
    cloudflare/cloudflared:latest tunnel --no-autoupdate --url http://n8n:5678

# 3. Прочитать URL вида https://...trycloudflare.com из логов.
#    Внимание: не показывать вывод на screen-share — лог содержит публичный URL.
docker logs testrag-cloudflared
```

**Rationale:** закрывает finding #6, плюс добавляет safety-предупреждение по R7 («trycloudflare URL leaks via screen-share») из `opus_result_risks.md`.

---

## P6 — README §Быстрый запуск: добавить sanity-step [LOW]

**Target:** `README.md` §Быстрый запуск (после шага 5, ≈ line 111).

**Proposed text (новый шаг 6):**
````markdown
6. Минимальная sanity-проверка перед демо:

```powershell
docker compose config --quiet
python -m pytest -p no:schemathesis
```

`docker compose config --quiet` — exit 0 без вывода; `pytest` — `15 passed` (см. `mvp-plan.md`).
````

**Rationale:** закрывает finding #10. Команды уже фигурируют в `docs/next-session.md §Минимальные команды` и `mvp-plan.md` — README ставит их в видимое место.

---

## P7 — README §Вопросы к заказчику: статус-маркеры [LOW]

**Target:** `README.md` §Вопросы к заказчику (lines 318–327).

**Proposed text:**
```markdown
## Вопросы к заказчику

- Какие типы документов и вопросов приоритетны для демо? **открыто**
- Какие внутренние регламенты можно использовать вместо открытых документов? **открыто**
- Какие источники считать допустимыми для юридических ссылок? **частично закрыто** — реестр в `manifests/NORMATIVE_SOURCE_MANIFEST.md`.
- Нужны ли разные права доступа для HR и юристов в MVP? **открыто**
- Где должны храниться логи: Supabase или Google Sheets? **закрыто** — Postgres (`request_logs`, `answer_feedback`, `review_queue`).
- Какой формат ответа удобнее: краткий вывод, цитаты, ссылки, список действий? **открыто**
- Кто будет ревьюить плохие ответы и с какой периодичностью? **открыто**
```

**Rationale:** закрывает finding #11. Один пункт уже отвечен инфраструктурой, не нужно держать как «вопрос».

---

## P8 — demo-runbook §Подготовка п.3: явный режим MISTRAL [LOW]

**Target:** `docs/demo-runbook.md` §Подготовка, пункт 3 (line 11).

**Current text:**
```markdown
3. Заполнить `TELEGRAM_BOT_TOKEN`, `ALLOWED_TELEGRAM_USER_IDS`, при наличии `MISTRAL_API_KEY`.
```

**Proposed text:**
```markdown
3. Заполнить `TELEGRAM_BOT_TOKEN`, `ALLOWED_TELEGRAM_USER_IDS` и `MISTRAL_API_KEY`.
   Без `MISTRAL_API_KEY` сервис работает в extractive-режиме (BM25 без векторов):
   `confidence` по тем же вопросам ниже, часть demo-кейсов попадает в refusal.
```

**Rationale:** закрывает finding #5. Без объяснения последствий «при наличии» провоцирует demo-провал.

---

## P9 — demo-runbook §Импорт n8n CLI: аннотация «только при первой установке» [LOW]

**Target:** `docs/demo-runbook.md` §Импорт n8n Через CLI (line 42).

**Proposed addition (перед текущим текстом раздела):**
```markdown
> Этот раздел нужен только при первой установке или после `docker compose down -v`.
> Если в `n8n.workflow_entity` уже есть активный `testrag-hr-legal-assistant`
> (это так в текущем deployment, см. `mvp-plan.md §Current Status`), пропустите раздел.
```

**Rationale:** закрывает finding #12. Снижает шанс повторного импорта с дублем `id`.

---

## P10 — README §Конфигурация .env: default DOCS_PATH на corpus [LOW]

**Target:** покрывается P1 (новый default уже там — `DOCS_PATH=/app/corpus`).

**Why отдельный пункт:** для трекинга — это N1 из `opus_result_next_docs_delta.md`. Закрывается тем же патчем.

**Status:** **closed-by-P1**. Отдельный edit не нужен.

---

## P11 — mvp-plan §Next Tasks: добавить owner [LOW]

**Target:** `mvp-plan.md` §Next Tasks, строка `[ ] Прогнать demo runbook end-to-end.` (line 37).

**Current text:**
```markdown
- [ ] Прогнать demo runbook end-to-end. Verify: HR-вопрос, legal-вопрос, low-confidence refusal и document draft проходят по ожидаемому сценарию.
```

**Proposed text:**
```markdown
- [ ] Прогнать demo runbook end-to-end. Owner: demo operator (по `opus_result_next_demo_script.md` + `opus_result_next_presenter_checklist.md`). Verify: HR-вопрос, legal-вопрос, low-confidence refusal и document draft проходят по ожидаемому сценарию.
```

**Rationale:** закрывает N2. Сигнализирует Codex/Opus, что этот пункт принадлежит человеку-оператору.

---

## Что НЕ патчится этим планом (известно, но out-of-scope)

- `docs/legal-document-prompts.md` — Opus task запрещает редактировать `docs/`. Этот файл, по предыдущему пасу, не имел открытых finding'ов.
- `docs/next-session.md` — finding #4 закрыт.
- `mvp-plan.md §Current Status corpus state` — finding #7 закрыт.
- README §Архитектура Mermaid — finding #9 закрыт.
- N3 (next-session.md дублирует mvp-plan §Done When) — оставляем, низкий приоритет.
- `manifests/MANIFEST.md` 8170 строк — не открыт в этом проходе из-за лимита Read. Если Codex сам обновляет MANIFEST под swap из `opus_result_followup_manifest_decision.md`, дополнительный аудит не требуется.

## Execution checklist для Codex

После применения P1–P9, P11:

1. `git diff README.md mvp-plan.md docs/demo-runbook.md` — проверить, что не зацепил соседние секции.
2. `markdownlint README.md mvp-plan.md docs/*.md` (если в проекте есть линтер) — отсутствие сломанных code fences.
3. Markdown preview всех трёх файлов в IDE — таблицы и кодовые блоки рендерятся.
4. `python -m pytest -p no:schemathesis` — должно остаться `15 passed`, документация не должна вызвать regression (но pytest на docs ничего не проверяет напрямую — это sanity на код).
5. Re-run `opus_result_next_docs_delta.md` cross-check вручную: статусы PARTIAL должны стать CLOSED для #1, #2, #3, OPEN → CLOSED для #5, #6, #8, #10, #11, #12.

## Verification (self-check)

- 9 ещё-открытых пунктов и 3 новых из предыдущего паса покрыты one-for-one.
- Для каждого: target file, section, current/proposed wording, priority, rationale.
- Priority калибрована: HIGH (2) — то, что сейчас ломает onboarding / показывает устаревший статус; MEDIUM (3) — структурные ссылки и cloudflared; LOW (5) — wording и аннотации.
- Codex может применять patches независимо — между P1–P11 нет dependency, кроме того, что P10 закрывается P1.
- Проектные файлы не редактировались.
