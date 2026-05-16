# Next Session

## Как начать следующую сессию

Скопируй в новый чат:

```text
Продолжаем проект D:\TestRag.

Контекст:
- MVP HR/legal RAG-ассистент. Aviation profile pass на 200 docs, MVP-44 (chunk_count=207, docs=48 в БД).
- Стек: FastAPI + Mistral + hybrid retrieval (BM25 + pgvector) → n8n (24 узла) → Telegram-бот @AIagentJu_bot.
- Документация: README.md, mvp-plan.md, docs/demo-runbook.md, docs/legal-document-prompts.md, docs/research/SYNTHESIS.md, docs/findings/.

Текущее состояние (HEAD `daa8795`, 2026-05-17 day):
- pytest 68/68 (+12 Sprint 1, +6 Sprint 1 fixes, +14 Sprint 2 /history+/docs+M7, +5 split+balance).
- Sprint 1 deployed + TG smoke ✓ через @AIagentJu_bot.
- Sprint 2 deployed:
  - M7 schema: answer_feedback +category +free_text +chunk_ids.
  - M5 команды: /help, /clear, /history, /docs.
  - N5 endpoint: GET /docs/summary.
- TG split: Format Answer split по \n\n/предложениям до 4000 chars, balanceTags. Workflow Last Part? If → keyboard только на is_last. Live smoke .tmp/smoke_split.py: 2 parts (3895+674 chars) через Bot API → message_ids [97,98] OK.
- Cloudflare tunnel: trycloudflare URLs эфемерны, пересоздавать процедурой из docs/demo-runbook.md.

Что осталось (Sprint 3, по приоритету):

1. **N1 follow-up question buttons** (отложен из Sprint 2). План:
   - Новый endpoint `GET /followup?request_log_id=X&idx=Y` → возвращает crafted question из request_logs.sources[Y].section.
   - storage.get_request_source(rl_id, idx).
   - Whitelist parser: callback `followup:<idx>:<rl_uuid>` (47 chars, fits в 64-byte лимит TG) → event_type='followup_request'.
   - Workflow: Followup? If → Resolve Follow-up HTTP → Set Question (Code) → Send Typing → Ask RAG API → ...
   - Send Answer refactor: с Telegram-node на HTTP node (sendMessage), чтобы inline_keyboard был dynamic — добавить 2 follow-up кнопки на основе sources[0..1].section + 2 feedback кнопки.

2. **N3 Human handover**: feedback:bad_human уже пишет category='human' + review_queue. Добавить:
   - Last 5 messages user'а → review_queue.context (новый jsonb column).
   - Confirmation user'у: «Ваш запрос направлен HR/Legal на ручную обработку».

3. **N4 Conversation threading**: thread_id в n8n (reply-to-message), prev 3 QA в retrieval.

4. **N2 Quick-actions**: «Уточнить» (top_k=10 rerun), «Развернуть» (full chunk).

5. **Retrieval regression** (документировано в docs/findings/2026-05-17-retrieval-aviation-pollution.md): aviation-pass переписал ВСЕ 200 файлов под авиа, включая HR-шаблоны. Теперь controlled-zone Q даёт top=02_hr_tmp_employment_contract.md score 0.937 вместо 01_hr_pol_safety. 4 варианта fix описаны там. Решение: пока документировать как known limitation демо (Mistral собирает корректный ответ из «не тех» source); Sprint 4 retrieval polish.

Sprint 2 TG-смок (если ещё не пробовала после `daa8795`):
1. `/help` → HTML список команд + примеры.
2. `/history` → «Последние N запросов» с историей (русское склонение).
3. `/docs` → «Корпус: 48 документов» + 8 категорий.
4. `Какие документы нужны для отправки dangerous goods авиатранспортом?` → typing → ответ (если короткий — 1 сообщение, если >4000 chars — split на 2-3 части с пометкой «часть N/M»). Кнопки 👍/👎 только на последней части.
5. Клик 👎 → 3 reason-кнопки (Неточно/Устарело/Нужен человек) меняют клавиатуру исходного сообщения → выбор → «Оценка принята.» + answer_feedback.category='inaccurate'.

Перед работой:
- Не выводить .env, токены, ключи в чат.
- После изменений python-кода: docker compose build rag-api && docker compose up -d --force-recreate rag-api && python -m pytest -p no:schemathesis (68/68).
- После изменений n8n workflow: MSYS_NO_PATHCONV=1 docker compose exec -T n8n n8n import:workflow --input=/workflows/hr-legal-rag-workflow.json --projectId=AAx39VT08WENfUYU && MSYS_NO_PATHCONV=1 docker compose exec -T n8n n8n update:workflow --active=true --id=testrag-hr-legal-assistant && docker compose up -d --force-recreate n8n.
- Перед TG-смоком: curl ${N8N_WEBHOOK_URL}healthz должен вернуть 200.
```

## Минимальные команды

```powershell
cd D:\TestRag
python -m pytest -p no:schemathesis  # 68 passed
docker compose config --quiet
docker compose up -d
curl http://localhost:8000/health    # chunk_count=207
curl 'http://localhost:8000/history?telegram_user_id=432751211&limit=5'
curl http://localhost:8000/docs/summary
python .tmp/smoke_split.py           # send synthetic 4000-char split to chat
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

## Workflow node count check

```powershell
docker compose exec -T postgres psql -U testrag -d testrag -tA -c "select jsonb_array_length(nodes::jsonb), active from n8n.workflow_entity where id='testrag-hr-legal-assistant';"
```

Ожидаемо: `24|t`. Если меньше — старый JSON, нужно re-import.

## Если cloudflare tunnel умер

`docker logs testrag-cloudflared` пусто или контейнер не запущен → URLs эфемерные. Процедура восстановления — `docs/demo-runbook.md` раздел «Локальный Telegram Webhook».
