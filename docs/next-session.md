# Next Session

## Как начать следующую сессию

Скопируй в новый чат:

```text
Продолжаем проект D:\TestRag.

Контекст:
- MVP HR/legal RAG-ассистент. Aviation profile pass на 200 docs, MVP-44 (chunk_count=207, docs=48 после Sprint 2 ingest).
- Стек: FastAPI + Mistral + hybrid retrieval (BM25 + pgvector) → n8n оркестратор (22 узла) → Telegram-бот @AIagentJu_bot.
- Документация: README.md, mvp-plan.md, docs/demo-runbook.md, docs/legal-document-prompts.md, docs/research/SYNTHESIS.md.

Текущее состояние (HEAD `ef23933`, 2026-05-17 day):
- pytest 63/63 (+12 Sprint 1, +6 Sprint 1 fixes, +14 Sprint 2).
- Sprint 1 deployed + smoke ✓ (TG controlled-zone question: HTML рендер с MD→HTML конверсией, typing, 2 кнопки 👍/👎 с drill-down на 👎).
- Sprint 2 deployed:
  - M7 schema: answer_feedback +category +free_text +chunk_ids (auto-pulled из request_logs.sources).
  - M5 команды: /help (HTML список), /clear (про stateless), /history (последние 5 из request_logs с русским склонением), /docs (8 категорий, total 48 docs).
  - N5 endpoint: GET /docs/summary с category-grouped count.
- Cloudflare tunnel: trycloudflare URLs эфемерны, пересоздавать процедурой из docs/demo-runbook.md.

Что осталось (Sprint 3, по приоритету):
1. **N1 follow-up question buttons** (отложен из Sprint 2): 2 кнопки «уточняющий вопрос» в Send Answer, на основе section заголовков top-3 chunks. Challenge: TG callback_data лимит 64 байта → encode index, lookup через request_log_id.sources в Whitelist при клике.
2. **N3 Human handover**: кнопка «🧑‍💼 Связать с HR» при low confidence или категории «human» → запись в review_queue с last 5 messages.
3. **N4 Conversation threading**: хранить thread_id в n8n (reply-to-message), подмешивать prev 3 QA в retrieval query.
4. **N2 Quick-actions**: «Уточнить» (rerun с top_k=10), «Развернуть» (full chunk вместо snippet).
5. Retrieval quality issue (вне Sprint roadmap): controlled-zone Q сейчас даёт top=02_hr_tmp_employment_contract.md score 0.426 вместо 01_hr_pol_safety.md score 0.97 как было раньше. Возможно MVP manifest изменился или chunks re-ingested после aviation pass. Проверить chunk_count vs docs_count в /health.

Sprint 2 TG-смок (если ещё не пробовала):
1. /help — ожидаем HTML список команд + примеры.
2. /history — ожидаем «Последние N запросов» с историей.
3. /docs — ожидаем «Корпус: 48 документов» + 8 категорий.
4. Любой вопрос → typing + HTML-ответ (с `<b>` вместо `**`) + плюрализация.
5. Клик 👎 → 3 reason-кнопки, выбор → answer_feedback.category=inaccurate/outdated/human.

Перед работой:
- Не выводить .env, токены, ключи в чат.
- После изменений python-кода: docker compose build rag-api && docker compose up -d --force-recreate rag-api && python -m pytest -p no:schemathesis (ожидаем 63/63).
- После изменений n8n workflow: MSYS_NO_PATHCONV=1 docker compose exec -T n8n n8n import:workflow --input=/workflows/hr-legal-rag-workflow.json --projectId=AAx39VT08WENfUYU && MSYS_NO_PATHCONV=1 docker compose exec -T n8n n8n update:workflow --active=true --id=testrag-hr-legal-assistant && docker compose up -d --force-recreate n8n.
- Перед TG-смоком проверить, жив ли cloudflare tunnel: curl ${N8N_WEBHOOK_URL}healthz должен вернуть 200.
```

## Минимальные команды

```powershell
cd D:\TestRag
python -m pytest -p no:schemathesis  # 63 passed
docker compose config --quiet
docker compose up -d
curl http://localhost:8000/health    # chunk_count=207, postgres_enabled=true
curl 'http://localhost:8000/history?telegram_user_id=432751211&limit=5'
curl http://localhost:8000/docs/summary
```

## Sprint 2 schema check

```powershell
docker compose exec -T postgres psql -U testrag -d testrag -tA -c "\d answer_feedback"
```

Ожидаемо: 9 columns (id, request_log_id, telegram_user_id, rating, comment, created_at, category, free_text, chunk_ids).

```powershell
docker compose exec -T postgres psql -U testrag -d testrag -tA -c "select category, free_text, jsonb_array_length(chunk_ids) from answer_feedback order by created_at desc limit 5;"
```

После TG-смока с 👎 → Неточно: должна быть строка с category='inaccurate', chunk_ids — массив uuid из request_logs.sources.

## Если cloudflare tunnel умер

`docker logs testrag-cloudflared` пусто или контейнер не запущен → URLs эфемерные. Процедура восстановления — `docs/demo-runbook.md` раздел «Локальный Telegram Webhook».
