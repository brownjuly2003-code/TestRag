# Opus Result Followup: Greeting & Small-Talk Response Contract

> Status 2026-05-16: Codex implemented the core contract for greetings, `/start`, empty input, and thanks in n8n. Off-topic small-talk remains a contract recommendation unless implemented later.

> Источник: `opus_result_followup_telegram_copy.md` (база wording'а), `opus_result_followup_greeting_route_triage.md` (UX gaps).
> Назначение: точный contract «вход → ответ → вызов RAG API да/нет» для 6 категорий пользовательского текста.
> Принцип: всё, что НЕ нормативный вопрос — отвечать локально без `/ask`. Это экономит latency + Mistral cost + не засоряет request_logs шумом.
> Никакие файлы не редактировались.

## Контрактная таблица (sum-up)

| # | Вход | Категория | Call /ask? | Ответ |
|---|------|-----------|------------|-------|
| C1 | `/start`, `/help` | command | НЕТ | greeting + scope |
| C2 | `привет`, `здравствуйте`, `добрый день`, `hi`, `hello` | small-talk greeting | НЕТ | short greeting |
| C3 | пустое сообщение / только пробелы / стикер без caption | empty | НЕТ | подсказка-уточнение |
| C4 | `спасибо`, `благодарю`, `thanks`, `thank you` | small-talk thanks | НЕТ | вежливое ack |
| C5 | off-topic («погода», «как дела», «что нового») | small-talk off-topic | НЕТ | scope-reminder |
| C6 | вопрос с нормативной формулировкой → `/ask` вернул `refused=true` или `confidence < MIN_CONFIDENCE` | low-confidence answer | ДА | refusal или low-conf postfix |

Любое сообщение, не подходящее под C1–C5, маршрутизируется на `/ask` как обычный domain question (включая короткие, но содержательные вопросы вроде «отпуск 28 дней?»).

## Routing-логика (псевдокод для Codex)

```javascript
// В n8n Whitelist node ИЛИ отдельном Code node «Classify»
const raw = (message.text || '').trim();
const lower = raw.toLowerCase();

// C1 — Telegram commands
if (raw === '/start' || raw === '/help' || raw.startsWith('/start ') || raw.startsWith('/help ')) {
  return { route: 'greeting', text: GREETING_TEXT };
}

// C2 — small-talk greetings
const GREETINGS = new Set(['привет','привет!','здравствуйте','здравствуй','добрый день','добрый вечер','доброе утро','hi','hello','hey','здарова','здарова!','салют']);
if (GREETINGS.has(lower)) {
  return { route: 'greeting', text: SHORT_GREETING_TEXT };
}

// C3 — empty / whitespace
if (raw === '') {
  return { route: 'empty', text: EMPTY_TEXT };
}

// C4 — thanks
const THANKS = new Set(['спасибо','спасибо!','благодарю','благодарю!','спс','thanks','thank you','thx']);
if (THANKS.has(lower)) {
  return { route: 'thanks', text: THANKS_TEXT };
}

// C5 — off-topic короткие small-talk
const OFFTOPIC = ['как дела','что нового','как ты','как погода','что умеешь','кто ты','о чем ты','о чём ты'];
if (OFFTOPIC.some(s => lower.includes(s))) {
  return { route: 'offtopic', text: OFFTOPIC_TEXT };
}

// default → ask RAG API
return { route: 'question', text: raw };
```

Опционально на стороне RAG API: handle `min_length` или короткие тексты (< 5 символов, < 2 слов) на отдельном `/smalltalk` endpoint, чтобы n8n не пришлось дублировать словари. Но в MVP — проще держать в n8n Whitelist/Classify, потому что:
- быстрее;
- не засоряет `request_logs`;
- не тратит Mistral quota.

## Тексты ответов

### C1 — Greeting (`/start`, `/help`)

```
Здравствуйте. Я — демо-ассистент по HR и юридическим вопросам.

Что я умею:
• Отвечать на нормативные вопросы со ссылками на ТК РФ, ГК РФ, ФЗ и приказы.
• Помогать определить тип документа и список недостающих полей.
• Готовить черновики кадровых приказов и договоров.

Что важно знать:
• Документы корпуса — синтетические образцы для демо.
• Нормативные ссылки реальные, но всегда сверяйте с юристом.
• Если данных мало — я честно отказываюсь, а не догадываюсь.

Задайте вопрос текстом.
```

### C2 — Small-talk greeting

```
Здравствуйте. Я отвечаю на HR и юридические вопросы со ссылками на ТК, ГК, ФЗ. Задайте вопрос — например: «Сколько длится испытательный срок?»
```

### C3 — Empty input

```
Не вижу текста вопроса. Сформулируйте, что нужно узнать — желательно с указанием темы: трудовой договор, отпуск, договор поставки, претензия, путевой лист, ПДн.
```

### C4 — Thanks

```
Пожалуйста. Если нужен следующий вопрос — задавайте.
```

### C5 — Off-topic small-talk

```
Я отвечаю только на HR и юридические темы по проиндексированной базе. Спросите про трудовой договор, отпуск, договор поставки, претензию, путевой лист или ПДн.
```

### C6 — Low-confidence postfix (после ответа `/ask` при `refused=false` AND `confidence < HIGH_CONF_THRESHOLD`)

Постфикс к ответу (НЕ заменяет ответ):

```
[Низкая уверенность] Источников по теме мало. Проверьте ответ перед использованием и при необходимости уточните формулировку.
```

### C6 alt — Refusal от RAG API (`refused=true`)

Wording уже в RAG API (`main.py:570`): «Не хватает надежных источников для ответа. Уточните вопрос или добавьте документ в базу знаний.»

**Suggestion для Codex:** заменить на расширенный wording из `opus_result_followup_telegram_copy.md §2A`:

```
В моей базе недостаточно проверенных источников по этому вопросу.

Что можно сделать:
• Переформулировать через номер статьи или закона (например: «ст. 70 ТК РФ»).
• Уточнить категорию документа.
• Обратиться к профильному специалисту, если тема выходит за рамки демо-корпуса.

Я не догадываюсь, когда источников нет.
```

---

## Pass/Fail criteria для каждой категории

### C1 (`/start`, `/help`)

- **Pass:** ответ содержит «Здравствуйте» И список «Что я умею» И слова «не юридическая консультация» ИЛИ «синтетические».
- **Fail:** пустой ответ; `/ask` вызван (в request_logs появилась запись с question='/start' или '/help'); ответ содержит «Confidence:» (значит, пошёл через Format Answer для обычного вопроса).
- **Verify (live):** SQL `select count(*) from request_logs where question in ('/start','/help');` после теста = 0.

### C2 (приветствие)

- **Pass:** ответ ≤ 250 символов, содержит «Здравствуйте» И один пример вопроса.
- **Fail:** ответ полный greeting (как C1) — это плохой UX для short greeting; пустой ответ; ответ через `/ask`.
- **Verify:** request_logs не пополнен; время от отправки до получения ответа < 1.5 сек.

### C3 (пустой/whitespace)

- **Pass:** ответ содержит «не вижу текста» ИЛИ «сформулируйте» ИЛИ «текста вопроса нет».
- **Fail:** `/ask` вызван с question='' (Pydantic откажет с 422 — ошибка пользователю); workflow прерывается; пустой ответ.
- **Verify:** SQL `select count(*) from request_logs where question='' OR question is null;` = 0.

### C4 (thanks)

- **Pass:** ответ содержит «Пожалуйста» ИЛИ «Рада/рад помочь» ИЛИ «Если нужен следующий вопрос».
- **Fail:** `/ask` вызван; ответ через Format Answer (с Confidence).
- **Verify:** request_logs без записи `question='спасибо'`.

### C5 (off-topic)

- **Pass:** ответ содержит «отвечаю только на HR» ИЛИ «юридические темы» И один пример темы.
- **Fail:** `/ask` вызван и вернул refusal — формально это тоже работает, но засоряет логи и расходует Mistral, **anti-pattern**.
- **Verify:** request_logs без записи на off-topic фразы; время ответа < 1 сек (нет ходки в RAG).

### C6 (low-confidence answer)

- **Pass (refused=true):** ответ содержит расширенный refusal wording + НЕТ инлайн-кнопок Good/Bad (на refusal оценивать нечего).
- **Pass (refused=false, low conf):** ответ + постфикс `[Низкая уверенность]` + inline keyboard есть.
- **Fail:** на `refused=true` отправлены кнопки Good/Bad; на low-confidence нет постфикса; пустой ответ.
- **Verify:** в `Send Answer` node при `refused=true` — Telegram message без `reply_markup`.

---

## Обязательно: где RAG API НЕ должен вызываться

| Категория | Почему НЕТ |
|-----------|------------|
| C1 `/start` | Команда Telegram — это UX, не информационный запрос. Mistral потратит токены на бесполезный refusal. |
| C2 greeting | Один-два слова приветствия не дадут retrieval; гарантированный refusal с confidence=0 — шум. |
| C3 empty | `AskRequest.question: Field(min_length=1)` отбросит. Лучше перехватить раньше. |
| C4 thanks | Бессмыслица для RAG. |
| C5 off-topic | Та же причина, что C2. |

**Net эффект** правила: ≈ 30–50% потенциальных вызовов `/ask` (greetings + thanks + off-topic) фильтруются на n8n уровне. Это:
- снижает Mistral cost ≈ на эту же долю;
- очищает `request_logs` от мусора (фильтрация лучше для метрик «доля refusal-ответов»);
- ускоряет ответ для типичных small-talk до < 1 сек.

---

## Edge cases

### EC1. Длинная фраза с «привет» в середине

`"привет можешь рассказать про отпуск"` — НЕ должен попадать в C2 (это вопрос с приветствием в начале). Чёткий маркер: словарь C2 проверяется через `set.has(lower)` (точное совпадение всей строки, не подстрока). Так что эта фраза идёт на `/ask` как question. **Pass.**

### EC2. Регистр

`"Привет"`, `"ПРИВЕТ"`, `"привет!"` — обрабатывается через `.toLowerCase()`. Восклицательный знак включён в словарь (`'привет!'`). Для надёжности можно `.replace(/[!?.,]+$/, '')` перед lookup.

### EC3. Эмодзи / стикеры / медиа

`message.text` может отсутствовать (только sticker, voice, photo). Текущий код: `text = message.text || callbackData || ''` → text = `''` → попадает в C3 empty.

**Suggestion:** если `message.sticker` есть, отвечать «Я понимаю только текст. Сформулируйте вопрос словами.»

### EC4. Цифры/спецсимволы

`"???"` — не в словарях, идёт на `/ask`. Pydantic пропустит (`min_length=1`). RAG вернёт refusal. OK.

### EC5. Mixed languages

`"hello, what about probation period?"` — текущий greeting set включает `'hello'` точным матчем, не префиксом. Эта строка не попадёт в C2, уйдёт на `/ask`. OK.

---

## Acceptance criteria summary (для Codex test plan)

| Test | Input | Expected route | Expected text contains | /ask called? |
|------|-------|----------------|------------------------|--------------|
| AC1.1 | `/start` | greeting | «Здравствуйте» AND «не юридическая консультация» | no |
| AC1.2 | `/help` | greeting | same | no |
| AC2.1 | `привет` | greeting-short | «Здравствуйте» AND пример вопроса | no |
| AC2.2 | `Привет!` | greeting-short | same | no |
| AC2.3 | `hello` | greeting-short | same | no |
| AC3.1 | `   ` (whitespace) | empty | «не вижу текста» | no |
| AC3.2 | (только sticker) | empty | «понимаю только текст» (если EC3 fix) | no |
| AC4.1 | `спасибо` | thanks | «Пожалуйста» | no |
| AC5.1 | `как дела` | offtopic | «отвечаю только на HR» | no |
| AC6.1 | `Сколько длится испытательный срок?` | question | «3 мес» AND «70» + sources | yes |
| AC6.2 | `Что такое неизвестная тема?` (refused) | question | refusal wording | yes |
| AC6.3 | `привет можешь рассказать про отпуск` | question | про отпуск + sources | yes |

Все 12 AC должны проходить **без** возврата пустого Telegram-сообщения.

## Verification (self-check)

- 6 категорий + edge cases покрывают все вход-кейсы, описанные в задаче (`привет`, `/start`, empty, thanks, off-topic, low-confidence).
- Чёткая граница «вызывать `/ask` / нет» для каждой категории — экономит latency, cost, и снимает silence-риск S4 (пустой answer на смыслово-пустой prompt).
- Pseudocode для Codex явный, словари приведены.
- 12 acceptance criteria готовы к автотесту.
- Тексты совместимы с `opus_result_followup_telegram_copy.md` и `opus_result_next_disclaimer.md`.
- Проектные файлы не редактировались.
