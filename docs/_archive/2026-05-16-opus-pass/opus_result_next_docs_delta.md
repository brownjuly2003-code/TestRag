# Opus Result Next: Docs Delta After Codex Pass

> Source: `opus_result_docs_consistency.md` — 12 исходных findings.
> Method: повторное чтение `README.md`, `mvp-plan.md`, `docs/demo-runbook.md`, `docs/next-session.md` после Codex-правок. Сравнение с original wording.
> Scope: оставить только ещё открытые / частично открытые пункты + новые расхождения, появившиеся после правок.

## Сводный статус

| # | Файл | Раздел | Severity | Статус |
|---|------|--------|----------|--------|
| 1 | README.md | §Текущий статус 136–148 | HIGH | ⚠️ PARTIAL |
| 2 | README/all | Supabase vs Postgres | HIGH | ⚠️ PARTIAL (osталось в §Конфигурация) |
| 3 | README.md | §Структура 113–128 | MEDIUM | ⚠️ PARTIAL |
| 4 | docs/next-session.md | Что сделано/Что дальше | HIGH | ✅ CLOSED |
| 5 | docs/demo-runbook.md | §Подготовка п.3 | LOW | 🔴 OPEN |
| 6 | docs/demo-runbook.md | cloudflared network 85–86 | MEDIUM | 🔴 OPEN |
| 7 | mvp-plan.md | §Current Status corpus state | MEDIUM | ✅ CLOSED |
| 8 | README.md | §Документация 130–134 | MEDIUM | 🔴 OPEN |
| 9 | README.md | §Архитектура Mermaid | MEDIUM | ✅ CLOSED |
| 10 | README.md | §Быстрый запуск | LOW | 🔴 OPEN |
| 11 | README.md | §Вопросы к заказчику 318–327 | LOW | 🔴 OPEN |
| 12 | docs/demo-runbook.md | §Импорт n8n CLI 42–61 | LOW | 🔴 OPEN |

Закрыто полностью: 3/12 (#4, #7, #9).
Закрыто частично: 3/12 (#1, #2, #3) — нужны точечные доправки.
Полностью открыто: 6/12 (#5, #6, #8, #10, #11, #12).

---

## Still-open findings (детально)

### #1 README §«Текущий статус» — PARTIAL [HIGH]

Что закрыто:
- `Тесты ... -> 15 passed` — обновлено (было 11).
- `Updated: 2026-05-16` есть.
- Добавлен пункт про manifest mode.

Что осталось:
- README не отражает фактическое состояние индекса: `documents=42`, `document_chunks=122` (mvp-plan §Current Status line 14). README только говорит «Добавлены стартовые демо-документы».
- Не указано, что n8n workflow **активирован**, а не только импортирован (mvp-plan: «workflow активирован, публичный webhook отвечает без ошибок»).
- Не упомянут whitelist для конкретного ID (это и не обязательно в публичном README, но в §статусе можно сказать «whitelist configured»).

Suggested patch (минимальное вмешательство):
```markdown
- В Postgres проиндексирован MVP-корпус: `documents=42`, `document_chunks=122` (см. `mvp-plan.md §Current Status`).
- n8n workflow `hr-legal-rag-workflow.json` импортирован и активирован.
```

---

### #2 Terminology Supabase vs Postgres — PARTIAL [HIGH]

Что закрыто:
- §MVP теперь `Postgres/pgvector` (line 17).
- Таблица §Подход к n8n line 47: `Postgres/pgvector | документы...` — FIXED.
- Mermaid диаграммы — оба узла переименованы в `Postgres pgvector` / `Postgres logs` (lines 160, 166).
- §RAG-логика, §Данные и индексация — упоминание Supabase убрано (lines 228, 237).

Что осталось:
- **§Конфигурация lines 281–282** всё ещё содержит:
  ```
  SUPABASE_URL=
  SUPABASE_SERVICE_ROLE_KEY=
  ```
  при этом ни `docker-compose.yml`, ни `rag-api/` их не используют (по mvp-plan, ingestion идёт в локальный Postgres).

Suggested patch §Конфигурация:
```env
# Локальный MVP (docker-compose)
TELEGRAM_BOT_TOKEN=
ALLOWED_TELEGRAM_USER_IDS=
MISTRAL_API_KEY=
MISTRAL_CHAT_MODEL=
MISTRAL_EMBEDDING_MODEL=
N8N_WEBHOOK_SECRET=
N8N_WEBHOOK_URL=                   # для live Telegram через tunnel
DOCS_PATH=/app/corpus
DOCS_MANIFEST_PATH=/app/manifests/MVP_CORPUS_FILES.txt
```

Если Supabase оставлен как production target, отдельный блок с явным «Production-only»:
```env
# Production-only (не используется в локальном docker-compose)
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
```

---

### #3 README §«Структура проекта» — PARTIAL [MEDIUM]

Что закрыто:
- `corpus/` — добавлен (line 120).
- `manifests/MVP_CORPUS_FILES.txt` — добавлен (line 121).

Что осталось не упомянуто (реально присутствует в `D:\TestRag\`):
- `manifests/MANIFEST.md` (200 docs с frontmatter — основа отбора корпуса).
- `manifests/NORMATIVE_SOURCE_MANIFEST.md` (реестр нормативных источников).
- `normative/` (зарезервированная директория).
- `prompts/` (промпты пакетной генерации).
- `pytest.ini`.
- `mvp-plan.md` сам по себе тоже не в дереве, хотя на него много ссылок.

Suggested patch §Структура — расширить блок:
```text
TestRag/
  docker-compose.yml
  mvp-plan.md
  sql/init.sql
  data/sample_docs/
  corpus/
  manifests/MANIFEST.md
  manifests/MVP_CORPUS_FILES.txt
  manifests/NORMATIVE_SOURCE_MANIFEST.md
  normative/
  prompts/
  docs/demo-runbook.md
  docs/legal-document-prompts.md
  docs/next-session.md
  n8n/workflows/hr-legal-rag-workflow.json
  rag-api/app/
  rag-api/tests/
  pytest.ini
```

---

### #5 demo-runbook §Подготовка п.3 — OPEN [LOW]

Текущая формулировка (line 11):
> «Заполнить `TELEGRAM_BOT_TOKEN`, `ALLOWED_TELEGRAM_USER_IDS`, при наличии `MISTRAL_API_KEY`.»

Wording «при наличии» ничего не объясняет про последствия отсутствия ключа. На демо без Mistral retrieval становится BM25-only, и Q1, Q7 могут выпасть в low confidence. Это эксплуатационная информация, не косметика.

Suggested patch:
```markdown
3. Заполнить `TELEGRAM_BOT_TOKEN`, `ALLOWED_TELEGRAM_USER_IDS` и `MISTRAL_API_KEY`.
   Без `MISTRAL_API_KEY` сервис работает в extractive-режиме (BM25 без векторов):
   confidence по тем же вопросам ниже, часть demo-кейсов попадёт в refusal.
```

---

### #6 demo-runbook cloudflared network — OPEN [MEDIUM]

Текущая команда (lines 85–86):
```powershell
docker run -d --name testrag-cloudflared --network testrag_default cloudflare/cloudflared:latest tunnel --no-autoupdate --url http://n8n:5678
```

Имя сети `testrag_default` зависит от того, как Compose v2 нормализует project-name. На Windows с `compose v2` оно станет `testrag-default` (через дефис), а не `testrag_default` (через подчёркивание). Команда упадёт `network testrag_default not found`.

Suggested patch — добавить предварительный шаг и пометить имя как переменное:
```powershell
docker network ls --filter "name=testrag" --format '{{.Name}}'
# Использовать имя из вывода (например testrag_default или testrag-default)
docker run -d --name testrag-cloudflared --network <network_name> `
    cloudflare/cloudflared:latest tunnel --no-autoupdate --url http://n8n:5678
```

---

### #8 README §Документация без mvp-plan / manifests — OPEN [MEDIUM]

Текущий список (lines 130–134) только 3 doc-файла. Нет `mvp-plan.md`, `manifests/MANIFEST.md`, `manifests/NORMATIVE_SOURCE_MANIFEST.md` — а на них опираются и corpus shortlist, и нормативная привязка.

Suggested patch:
```markdown
- [MVP Plan](mvp-plan.md) — живой статус MVP: current state, next tasks, done-when.
- [Manifest корпуса](manifests/MANIFEST.md) — 200 демо-документов: doc_id, тип, департамент, приоритет.
- [Manifest нормативных источников](manifests/NORMATIVE_SOURCE_MANIFEST.md) — реестр ТК, ГК, ФЗ с recommended_chunks.
- [Demo Runbook](docs/demo-runbook.md) — как показать локальное демо.
- [Legal Document Prompts](docs/legal-document-prompts.md) — prompt для классификации юр/HR-документов.
- [Next Session](docs/next-session.md) — стартовый prompt для новой сессии.
```

---

### #10 README §Быстрый запуск без pytest/config — OPEN [LOW]

Текущий quickstart (lines 51–111) включает шаги 1–5, но не шаг про `docker compose config --quiet` и `python -m pytest`. Эти команды есть в `mvp-plan.md` и `docs/next-session.md §Минимальные команды` — README отстаёт.

Suggested patch (вставить после шага 5):
```markdown
6. Минимальная sanity-проверка перед демо:

```powershell
docker compose config --quiet
python -m pytest -p no:schemathesis
```
```

---

### #11 README §Вопросы к заказчику — OPEN [LOW]

Lines 318–327: список из 7 вопросов без статусов. Один пункт уже фактически закрыт: «Где должны храниться логи: Supabase или Google Sheets?» — логи в Postgres (mvp-plan §Current Status, README §Подход к n8n).

Один пункт частично закрыт: «Какие источники считать допустимыми для юридических ссылок?» — есть `manifests/NORMATIVE_SOURCE_MANIFEST.md`.

Suggested patch — добавить статус-маркер каждому пункту, например:
```markdown
- Какие типы документов и вопросов приоритетны для демо? **открыто**
- Какие внутренние регламенты можно использовать вместо открытых документов? **открыто**
- Какие источники считать допустимыми для юридических ссылок? **частично закрыто — `manifests/NORMATIVE_SOURCE_MANIFEST.md`**
- Нужны ли разные права доступа для HR и юристов в MVP? **открыто**
- Где должны храниться логи: Supabase или Google Sheets? **закрыто — Postgres**
- Какой формат ответа удобнее: краткий вывод, цитаты, ссылки, список действий? **открыто**
- Кто будет ревьюить плохие ответы и с какой периодичностью? **открыто**
```

---

### #12 demo-runbook §«Импорт n8n Через CLI» — OPEN [LOW]

Lines 42–61: текущая аннотация (line 44):
> «Если n8n уже запущен в Docker Compose, workflow и Telegram credential можно импортировать без UI.»

Эта подача предполагает, что CLI-импорт — нормальный flow. В реальности (mvp-plan: workflow активирован) повторно запускать `n8n import:workflow` не нужно и опасно (потенциальный дубль `id=testrag-hr-legal-assistant`).

Suggested patch — добавить annotation в начало раздела:
```markdown
> Этот раздел нужен только при первой установке или после `docker compose down -v`.
> Если `n8n.workflow_entity` уже содержит активный `testrag-hr-legal-assistant`
> (это так в текущем deployment, см. `mvp-plan.md §Current Status`), пропустите шаг.
```

---

## Новые расхождения, появившиеся после Codex-правок

### N1. README §Конфигурация default `DOCS_PATH=/app/data/sample_docs`, но live state — corpus [LOW]

Line 285 в `.env`-блоке: `DOCS_PATH=/app/data/sample_docs`. По mvp-plan текущий runtime запущен с corpus (`chunk_count=122`). Это не контр-факт (default ≠ runtime override), но новичок, копирующий `.env.example` и не читающий §Быстрый запуск п.2, получит маленький индекс.

Suggested patch — поменять default в `.env`-блоке README на manifest mode и добавить комментарий:
```env
# Default: MVP-корпус через manifest. Чтобы вернуться на минимальный sample —
# DOCS_PATH=/app/data/sample_docs, DOCS_MANIFEST_PATH=
DOCS_PATH=/app/corpus
DOCS_MANIFEST_PATH=/app/manifests/MVP_CORPUS_FILES.txt
```

Низкий приоритет (поведение runtime не ломается, только UX setup).

### N2. mvp-plan.md §Next Tasks: «Прогнать demo runbook end-to-end» без owner / due [LOW]

Line 37: `[ ] Прогнать demo runbook end-to-end.` — это и есть текущая Opus-таска по подготовке демо-сценария. Без указания owner может конфликтовать с Opus/Codex параллелизмом.

Suggested patch — добавить заметку:
```markdown
- [ ] Прогнать demo runbook end-to-end. Owner: demo operator (после применения
  `opus_result_next_demo_script.md` и `opus_result_next_presenter_checklist.md`).
```

### N3. docs/next-session.md §«Что нужно делать дальше» п.4 ≡ Done When [ ] [LOW]

Next-session line 34: «Проверить live Telegram happy path для whitelist-пользователя» — дублирует mvp-plan §Done When `[ ] Telegram-бот отвечает...` и §Next Tasks `[ ] Проверить live Telegram happy path`. Не противоречит, но создаёт три источника правды для одного действия. Это та же проблема, что описывалась в original finding #4 (которая в целом закрыта).

Низкий приоритет, можно оставить.

---

## Что не покрыто этим обзором

- Изменения в `rag-api/app/` и `sql/init.sql` (запрещено к чтению по `opus_task.md`).
- `docker-compose.yml`, `.env`, `.env.example` (запрещено).
- Содержание `manifests/MANIFEST.md` 8170 строк (не открывается из-за лимита; ссылки в README не проверены поштучно).

## Verification

- Все файлы прочитаны заново после Codex-правок (`README.md`, `mvp-plan.md`, `docs/demo-runbook.md`, `docs/next-session.md`).
- Каждый из 12 findings из `opus_result_docs_consistency.md` повторно сравнён с текущим текстом по строкам.
- Закрытые пункты (#4, #7, #9) явно отмечены и не дублируются в open list.
- Никакие проектные файлы не редактировались.
