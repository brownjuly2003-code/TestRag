# Next Session

## Как начать следующую сессию

Скопируй в новый чат:

```text
Продолжаем проект D:\TestRag.

Контекст:
- Это MVP HR/legal RAG-ассистента по ТЗ из PDF.
- n8n нужен как self-hosted оркестратор, не покупаем n8n Cloud.
- RAG API: FastAPI, Mistral, hybrid retrieval = BM25 + pgvector.
- База: Postgres/pgvector через Docker Compose.
- Telegram bot: токен лежит только в локальном .env, его не выводить.
- Документация: README.md, mvp-plan.md, docs/demo-runbook.md, docs/legal-document-prompts.md.
- MVP-корпус включается безопасно через DOCS_PATH + DOCS_MANIFEST_PATH, чтобы не индексировать все 200 corpus-файлов случайно.

Что уже сделано:
- docker-compose.yml для n8n + Postgres/pgvector + rag-api.
- RAG API с /health, /ask, /feedback, /document/type-detection.
- BM25 retriever и confidence policy.
- sample docs в data/sample_docs и manifest shortlist в manifests/MVP_CORPUS_FILES.txt.
- SQL init schema в sql/init.sql.
- n8n workflow JSON в n8n/workflows/hr-legal-rag-workflow.json.
- n8n IF-маршрутизация исправлена и активный workflow переимпортирован: `Authorized?` true -> `Feedback?`, false -> `Send Denied`; `Feedback?` true -> `Send Feedback`, false -> `Ask RAG API`.
- n8n direct-reply маршрут добавлен: `привет`, `/start`, пустые сообщения и благодарности отвечают без `/ask`; n8n attribution отключена на Telegram send-узлах.
- ingestion в Postgres: chunks + Mistral embeddings + document_chunks; измененные документы переиндексируются, отсутствующие embeddings дозаполняются.
- Mistral embeddings HTTP-ошибки не валят `/health` и `/ask`: RAG продолжает работать через текстовый retrieval.
- реальные логи request_logs, answer_feedback, review_queue.
- pytest: 25 тестов проходят.
- Текущий расширенный corpus health: `/health` -> `chunk_count=135`, `postgres_enabled=true`, `mistral_enabled=true`, `embeddings_enabled=true`.
- Корпус по испытательному сроку исправлен: продление испытательного срока не допускается.
- Opus handoff: исходные отчеты `opus_result_*.md`, следующий набор `opus_result_next_*.md`, follow-up отчеты `opus_result_followup_*.md`; часть follow-up файлов была подготовлена до Codex-фикса и сохранена как pre-fix triage/spec.
- Aviation profile pass (2026-05-16, коммиты `7c6951a` + `cfd2437`): 200 corpus-файлов перепрофилированы под авиагрузовую компанию. Все категории (01_hr policies, 02_hr templates, 03_legal contracts, 04_legal claims, 05_tlog, 06_comp, 07_faq) содержат AWB/MAWB/HAWB, controlled zone, aviation security, dangerous goods, GHA, cutoff, ULD. Добавлена секция «Рабочие доказательства, сроки и эскалация» во все 200 файлов. Roadmap в `aviation-corpus-tasks/01-10`.
- Структурные инварианты после aviation pass: `manifest_targets=200`, `corpus_files=200`, `missing=0`, `extra=0`, `missing_sections=0`, `frontmatter_issues=0`, `protected_issues=0`, `broken_corpus_refs=0`, aviation coverage 100% по всем 7 категориям.
- TG E2E подтверждён 2026-05-16/17: «привет» direct-reply OK, aviation Q «controlled zone» полный RAG-путь OK через @AIagentJu_bot, ответ с aviation-grounded content (controlled zone, AWB, dangerous goods, aviation security) и source attribution.
- RAG fix (2026-05-17 `e26a7da`/`4545982`): Mistral cautious lead-in («Данных недостаточно. Однако...») больше не обрезается к refused. 429 от free tier теперь graceful degrade на build_grounded_answer. Helper `is_pure_refusal()` вынесен с 4 unit-тестами. Golden Q 10/10 PASSED.
- MVP-корпус расширен до 44 файлов (2026-05-17 `7a798ec`): добавлены attendance, safety, training, business_trip, data_retention, faq_dismissal — покрывают controlled zone / aviation security / dangerous goods / retention / dismissal с пропуском demo Qs. chunk_count 179→207.
- TG keyboard fix (2026-05-17): underscore escape в Format Answer (TG Markdown V1 ел `_` в filenames), dedup sources, и `replyMarkup` перенесён из `additionalFields` в top-level params (root cause «кнопок не видела»). Кнопки временные «👍 Полезно / 👎 Неточно / 📋 Нужны источники» — будут изменены по research-синтезу.
- Bot UX research завершён (2026-05-17): запрошены параллельно Kimi и Codex, оба независимых прохода сохранены в `docs/research/2026-05-17-{kimi,codex}-bot-ux.md`. Консенсусный синтез с приоритизацией в `docs/research/SYNTHESIS.md`. Sprint-планы добавлены в `mvp-plan.md` (раздел Bot UX Roadmap).

Что нужно делать дальше:
1. Проверить, запущен ли Docker Desktop.
2. Для минимального demo оставить DOCS_PATH=/app/data/sample_docs; для MVP-корпуса поставить DOCS_PATH=/app/corpus и DOCS_MANIFEST_PATH=/app/manifests/MVP_CORPUS_FILES.txt.
3. Запустить docker compose up --build или пересоздать rag-api после смены DOCS_PATH. Содержание корпуса теперь aviation-themed: ingestion перечитает 38 MVP-файлов и пересчитает embeddings.
4. Прогнать aviation golden-questions из docs/demo-runbook.md (раздел «Aviation demo questions») и зафиксировать confidence/sources.
5. Проверить live Telegram happy path для whitelist-пользователя: `привет` и `/start` отвечают direct reply без n8n-приписки, доменный вопрос вызывает `/ask`.
6. Проверить feedback-кнопки: good/bad пишутся в answer_feedback, bad попадает в review_queue.
7. Прогнать docs/demo-runbook.md end-to-end.

Перед работой:
- Не выводить .env и секреты.
- После изменений запускать python -m pytest.
- Если трогаешь Docker, проверять docker compose config --quiet.
```

## Минимальные команды

```powershell
cd D:\TestRag
python -m pytest -p no:schemathesis
docker compose config --quiet
docker compose up --build
```

Если `docker compose up --build` падает на подключении к `dockerDesktopLinuxEngine`, сначала запустить Docker Desktop.
