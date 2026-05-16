# Bot UX Research Synthesis (Kimi + Codex, 2026-05-17)

Два независимых research-прохода: `2026-05-17-kimi-bot-ux.md` (Kimi) и `2026-05-17-codex-bot-ux.md` (Codex). Сводка консенсусных рекомендаций — где оба согласны, это shippable-must-have. Где один — это noted, но не блокер.

## Консенсус: MUST-HAVE для shippable MVP

| # | Рекомендация | Kimi | Codex | Текущее состояние |
|---|---|---|---|---|
| M1 | **Conditional/multi-step feedback**: 👎 → category buttons (неточно/устарело/не по теме/нужен человек) → optional free-text | ✅ | ✅ | ❌ статичные 3 кнопки |
| M2 | **Always-on inline citations**, не за кнопкой. Каждый ответ заканчивается блоком «Источники» с doc names + версиями | ✅ | ✅ | ⚠️ есть в тексте, но + кнопка «📋 Нужны источники» — антипаттерн |
| M3 | **Typing indicator** (`sendChatAction('typing')`) до retrieval/LLM — иначе бот кажется зависшим | ✅ | ✅ | ❌ нет |
| M4 | **HTML formatting** (не MarkdownV2 — слишком хрупко для динамических цитат). Bold для выводов, `code` для статей/пунктов, expandable blockquote для длинных правовых выдержек | ✅ | ✅ | ⚠️ сейчас default markdown V1, потерян |
| M5 | **Команды**: `/help`, `/clear`, `/history` (последние 5-10) — стандарт BotFather | ✅ | ✅ | ❌ только `/start` |
| M6 | **Confidence behavioral, не числовой**: «Найдено 3 документа» вместо «уверенность 73%» | (n/a) | ✅ | ❌ показываем confidence как число 0-1 |
| M7 | **Observability**: log chunk_ids, citation set, feedback category, time-to-first-token, retrieval latency | ✅ | ✅ | ⚠️ есть request_logs, нет chunk_ids в feedback |

## Консенсус: nice-to-have

- N1 Follow-up question buttons (2-3 контекстных suggested вопросов после ответа)
- N2 Quick-actions row («Уточнить», «Развернуть», «Создать задачу HR»)
- N3 Human handover (кнопка «🧑‍💼 Связать с HR/Legal» при низкой уверенности или «нужен человек»)
- N4 Conversation threading (reply-to-message с context из предыдущих 3 QA)
- N5 `/docs` — список разделов корпуса

## Анти-паттерны (убрать)

- A1 ❌ **Кнопка «Нужны источники»** — sources должны быть всегда inline. **Удалить** из текущего workflow.
- A2 ❌ Confidence как сырое % число
- A3 ❌ MarkdownV2 в динамическом контенте (escape-fragile)
- A4 ❌ Длинный disclaimer ДО ответа (1 строка после — OK)
- A5 ❌ Static 3 кнопки feedback без conditional drill-down
- A6 ❌ Nested меню 3+ уровней
- A7 ❌ Free-text feedback обязательный после каждого ответа

## Приоритезированный roadmap (после aviation pass)

### Sprint 1 — bot polish must-have (0.5–1 день)

- [ ] **M2 + A1**: Удалить кнопку «📋 Нужны источники», sources уже всегда inline в Format Answer. Кнопок 2: «👍 Полезно» / «👎 Неточно».
- [ ] **M3**: Добавить `sendChatAction('typing')` в начало n8n workflow перед `Ask RAG API`.
- [ ] **M4**: Перейти на `parse_mode='HTML'` в Send Answer. Update Format Answer JS: `**bold**` → `<b>`, filenames в `<code>`, citations как `<a href="">...</a>`.
- [ ] **M6**: Убрать вывод «Confidence: 1» в текст. Вместо — behavioral подсказка («Найдено N релевантных документов»).
- [ ] **M1 шаг 1**: При нажатии 👎 показать 3 reason-кнопки (Неточно/Устарело/Нужен человек). Записать в `answer_feedback` с категорией.

### Sprint 2 — UX uplift (1–2 дня)

- [ ] **M5**: Команды `/help`, `/clear`, `/history`. `/history` тянет из `request_logs` последние 5 запросов юзера.
- [ ] **M7**: Расширить `answer_feedback` схему: `chunk_ids` (jsonb array), `category` (enum), `free_text` (text nullable). Привязка feedback к ретривлу.
- [ ] **N1**: Mistral-вызов на генерацию 2 follow-up вопросов из top-3 chunks, добавить как кнопки.
- [ ] **N5**: `/docs` — высчитывать unique разделы из MVP-корпуса (по `category` frontmatter), выводить как list.

### Sprint 3 — production polish (1–2 дня)

- [ ] **N3**: Human handover. При conf<MIN или нажатии «Нужен человек» — кнопка «🧑‍💼 Связать с HR» (записать в `review_queue` с последними 5 сообщениями).
- [ ] **N4**: Conversation threading. В n8n хранить `thread_id` (reply-to-message), на reply подмешивать prev 3 QA в retrieval query.
- [ ] **N2**: Quick-actions «Уточнить» (rerun с extended top_k), «Развернуть» (full chunk вместо snippet).

## Что НЕ делаем (явно отказ)

- ❌ MarkdownV2 — выбрали HTML (Codex и Kimi оба категорично против)
- ❌ Confidence как `0.73` в UI — убираем
- ❌ Voice/audio messages — для legal text не критично
- ❌ Multi-language switch — корпус русский, аудитория русская
- ❌ RAGAs/full eval dashboard — overkill для demo
