# Next Session

## Как начать следующую сессию

Скопируй в новый чат:

```text
Продолжаем проект D:\TestRag.

Контекст:
- MVP HR/legal RAG-ассистент. Aviation profile pass на 200 docs, MVP-44 (chunk_count=207, docs=48 в БД).
- Стек: FastAPI + Mistral + hybrid retrieval (BM25 + pgvector + section-keyword rerank) → n8n (28 узлов) → Telegram-бот @AIagentJu_bot.
- Документация: README.md, mvp-plan.md, docs/demo-runbook.md, docs/legal-document-prompts.md, docs/research/SYNTHESIS.md, docs/findings/.

Текущее состояние (HEAD после ТЗ-критика sweep, 2026-05-17 EOS):
- pytest 101/101 (+5 /followup API + 9 N1 workflow + 5 N3 + 6 N4 + 8 ТЗ-критика поверх 68 baseline).
- Sprint 1 deployed + TG smoke ✓ через @AIagentJu_bot.
- Sprint 2 deployed:
  - M7 schema: answer_feedback +category +free_text +chunk_ids.
  - M5 команды: /help, /clear, /history, /docs.
  - N5 endpoint: GET /docs/summary.
- Sprint 3 N1 deployed (uncommitted, ждёт TG live smoke):
  - GET /followup?request_log_id=X&idx=Y → crafted question из request_logs.sources[idx]. Handles invalid UUID → 404.
  - PostgresStore.get_request_source(rl, idx) ловит psycopg.errors.InvalidTextRepresentation → None.
  - Whitelist: парсит `followup:<idx>:<rl>` (47 chars total, fits 64-byte TG limit) → event_type='followup_request'.
  - Workflow 28 узлов (+4): Followup? If, Resolve Follow-up, Send Typing Followup, Ask RAG Followup. Bad Clarify? no → Followup? → (yes → Resolve → Send Typing FU → Ask RAG FU → Format Answer) / (no → Direct Reply?).
  - Send Answer: телеграм-узел → HTTP sendMessage с dynamic reply_markup из $json.inline_keyboard (Format Answer строит keyboard на is_last: 2 follow-up + 2 feedback). Non-last parts → inline_keyboard=null.
  - Format Answer dedup сохраняет _originalIdx → callback_data использует НЕ-deduped позицию в request_logs.sources.
- TG split: Format Answer split по \n\n/предложениям до 4000 chars, balanceTags. Workflow Last Part? If → keyboard только на is_last. Live smoke .tmp/smoke_split.py: 2 parts (3895+674 chars) через Bot API → message_ids [97,98] OK.
- Cloudflare tunnel: trycloudflare URLs эфемерны, текущий `brooklyn-candidate-supplemental-abs.trycloudflare.com` жив. Пересоздавать процедурой из docs/demo-runbook.md.

Что осталось (Sprint 3, по приоритету):

1. ✅ Sprint 3 N1+N3+N4 — DONE (см. mvp-plan.md + git log).
2. ✅ ТЗ-критика 12 пунктов закрыта (см. docs/research/2026-05-17-architecture-critique-tz.md).

**Что осталось (Sprint 4, по приоритету):**

3. **Retrieval polish (issue #1 pollution)**: re-profile aviation pass только для tlog/safety/comp файлов, HR-шаблоны вернуть к pre-aviation. Цель — поднять Hit@1 с 0.22 до ≥0.6, MRR с 0.28 до ≥0.55. Eval baseline в `.tmp/eval_baseline.json`. 3-5 часов.

4. **Eval-driven regression gate**: после Sprint 4 retrieval polish добавить `pytest scripts/test_eval_regression.py` который читает `.tmp/eval_baseline.json` и проваливается если MRR упал ниже baseline.

5. **N2 Quick-actions** (Sprint 5): «Уточнить» (top_k=10 rerun), «Развернуть» (full chunk).

6. **Backlog: prev-N-QA в retrieval query** (was N4 part 2). Идея: расширить /ask payload `recent_questions[]` или server-side тянуть last 3 QA для user → конкатить в query текст перед embedding. Риск: сбивает hybrid BM25 hit на основном вопросе. Нужен ablation A/B на golden-questions через `scripts/eval_retrieval.py` перед merge.

7. **Document type filter в /ask** (Sprint 4 nice-to-have): optional `document_type: str` параметр → ограничивает retrieval по metadata.document_type. Сейчас все запросы идут глобально.

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
python -m pytest -p no:schemathesis  # 101 passed
docker compose config --quiet
docker compose up -d
curl http://localhost:8000/health    # chunk_count=207
curl 'http://localhost:8000/history?telegram_user_id=432751211&limit=5'
curl http://localhost:8000/docs/summary
# N1 smoke: real rl_id из request_logs (см. ниже)
curl 'http://localhost:8000/followup?request_log_id=<uuid>&idx=0'
python scripts/smoke_followup.py     # API-only E2E N1
# TG E2E smoke (user account через telethon, нажимает 📎/👎/🧑‍💼)
python scripts/smoke_tg_e2e.py       # читает D:/MCP/telegram-mcp/.env
python .tmp/smoke_split.py           # send synthetic 4000-char split to chat
# Eval baseline (critique #8) — обновлять перед/после Sprint 4
python scripts/eval_retrieval.py --output .tmp/eval_baseline.json
curl 'http://localhost:8000/metrics?window_hours=168'   # critique #12 observability
```

## TG E2E через telegram-mcp / Telethon

Установлен chigwell/telegram-mcp в `D:/MCP/telegram-mcp/`. Конфиг в `~/.claude.json` (`claude mcp list` → `telegram-mcp: ✓ Connected`). Сессия — StringSession для @AIagentJu_bot whitelist (id=432751211, имя Julia).

`scripts/smoke_tg_e2e.py` гоняет полный E2E через Telethon (user account):
1. send_message «Что такое controlled zone?»
2. wait reply → verify N4 `reply_to_msg_id` == user msg_id ✓
3. inspect inline_keyboard → 2 📎 follow-up + 2 👍/👎 ✓
4. click первой 📎 → wait second reply (N1)
5. click 👎 → edit reply markup → 3 reason buttons (Sprint 1)
6. click 🧑‍💼 → wait ACK «Ваш запрос направлен HR/Legal на ручную обработку» (N3) ✓
7. select review_queue order by created_at desc → `human|5`

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
