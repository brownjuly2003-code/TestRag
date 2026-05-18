# Opus Result Followup: Telegram Regression Test Spec

> Status 2026-05-16: Codex implemented the critical workflow regression coverage in `rag-api/tests/test_n8n_workflow.py` and added embeddings HTTP-fallback tests in `rag-api/tests/test_llm.py`. The remaining suites are backlog recommendations.

> Контекст инцидента: «привет» в Telegram → ответа нет. Static-триаж в `opus_result_followup_greeting_route_triage.md` указывает на 10 silence-points; наиболее вероятные — IF node schema mismatch (n8n v1 vs v2 filter conditions), inline keyboard structure, legacy `$node` access, и UX gap (greeting не обрабатывается отдельно).
> Назначение: концептуальные тест-кейсы, которые Codex должен **добавить или прогнать** в `rag-api/tests/` и (опционально) в новом `n8n/tests/` — без правки текущих файлов от Opus.
> Никакие тестовые файлы я не редактировал. Спецификация — текстовая, Codex её реализует.

## Существующие тесты (baseline для сверки)

`rag-api/tests/`:
- `test_api.py` — 7 тестов /health, /ask, /feedback, /document/type-detection.
- `test_ingestion.py` — ingestion.
- `test_n8n_workflow.py` — **1 тест**: `test_if_nodes_use_n8n_v2_filter_conditions` ожидает v2-формат IF nodes (`combinator + conditions[].leftValue/rightValue/operator`).
- `test_rag.py` — retrieval.

**Текущее наблюдение после Codex fix:** `n8n/workflows/hr-legal-rag-workflow.json` и `rag-api/tests/test_n8n_workflow.py` синхронизированы на v2-формате IF nodes (`combinator + conditions[].leftValue/rightValue/operator`). Workflow также содержит direct-reply ветку для greeting/empty/thanks.

Этот mismatch — самостоятельный baseline для всех новых тестов: workflow JSON и test_n8n_workflow.py должны быть в одном schema.

## Test suite 1 — Workflow JSON static assertions

**Файл:** `rag-api/tests/test_n8n_workflow.py` (расширить существующий).

### T1.1 IF nodes используют v2 schema (уже есть)

Существующий тест. Codex: **запустить и убедиться, что pass**. Если fail → исправить workflow JSON, не тест.

### T1.2 Inline keyboard format корректный

```python
def test_send_answer_uses_supported_inline_keyboard_shape():
    workflow = _load_workflow()
    nodes = {n["name"]: n for n in workflow["nodes"]}
    send_answer = nodes["Send Answer"]
    additional = send_answer["parameters"]["additionalFields"]

    assert additional["replyMarkup"] == "inlineKeyboard"
    inline = additional["inlineKeyboard"]
    rows = inline["rows"]
    assert isinstance(rows, list) and len(rows) >= 1

    # n8n nodes-base telegram v1.2 expects each row as { "buttons": [...] }
    # NOT { "row": { "buttons": [...] } }
    for row in rows:
        assert "buttons" in row, "Row must use 'buttons' key directly (no 'row' wrapper)"
        assert isinstance(row["buttons"], list)
        for btn in row["buttons"]:
            assert "text" in btn
            assert "additionalFields" in btn
            assert "callback_data" in btn["additionalFields"]
```

**Why:** silence-point S1 из триажа. Текущая `rows[i].row.buttons` структура — нестандартная; Telegram API отклоняет malformed `reply_markup` → silence.

### T1.3 Code nodes не используют legacy `$node[...]` access

```python
def test_code_nodes_use_modern_node_reference():
    workflow = _load_workflow()
    for node in workflow["nodes"]:
        if node["type"] != "n8n-nodes-base.code":
            continue
        js = node["parameters"]["jsCode"]
        assert "$node[" not in js, (
            f"Node '{node['name']}' uses legacy $node['...'] access. "
            "Use $('...').first().json in n8n v1.x."
        )
```

**Why:** silence-point S2. `$node['Whitelist'].json.chat_id` в Format Answer / Format Feedback может вернуть undefined → Send Answer fails «chat not found».

### T1.4 Все Telegram-node ссылки credential ID consistent

```python
def test_telegram_credentials_consistent():
    workflow = _load_workflow()
    expected = {"id": "testrag-telegram-api", "name": "TestRag Telegram Bot"}
    for node in workflow["nodes"]:
        if node["type"] in ("n8n-nodes-base.telegramTrigger", "n8n-nodes-base.telegram"):
            assert node["credentials"]["telegramApi"] == expected
```

**Why:** silence-point S7 (credential mismatch). Защищает от случайного переименования.

### T1.5 RAG_API_URL используется в HTTP nodes

```python
def test_http_nodes_use_rag_api_url_env():
    workflow = _load_workflow()
    nodes = {n["name"]: n for n in workflow["nodes"]}
    for name in ("Ask RAG API", "Send Feedback"):
        url = nodes[name]["parameters"]["url"]
        assert "$env.RAG_API_URL" in url, f"{name} must use $env.RAG_API_URL"
```

**Why:** silence-point S9 (env mismatch). Защищает от прописывания `http://localhost:8000` напрямую (не резолвится из контейнера n8n).

### T1.6 TelegramTrigger подписан на оба типа updates

```python
def test_telegram_trigger_subscribes_to_message_and_callback():
    workflow = _load_workflow()
    nodes = {n["name"]: n for n in workflow["nodes"]}
    updates = nodes["TelegramTrigger"]["parameters"]["updates"]
    assert set(updates) >= {"message", "callback_query"}
```

**Why:** S8 — если обновлено только `callback_query`, плейн text не дойдёт.

### T1.7 Connections: Authorized?:false → Send Denied, true → Feedback?

```python
def test_routing_connections_are_correct():
    workflow = _load_workflow()
    conn = workflow["connections"]

    # Authorized? true (index 0) → Feedback?
    auth_main = conn["Authorized?"]["main"]
    assert auth_main[0][0]["node"] == "Feedback?"
    # Authorized? false (index 1) → Send Denied
    assert auth_main[1][0]["node"] == "Send Denied"

    # Feedback? true (index 0) → Send Feedback (HTTP)
    fb_main = conn["Feedback?"]["main"]
    assert fb_main[0][0]["node"] == "Send Feedback"
    # Feedback? false → Ask RAG API
    assert fb_main[1][0]["node"] == "Ask RAG API"
```

**Why:** регрессия на структуру маршрутизации. Если кто-то поменяет порядок branches IF — silence для какого-то пути.

---

## Test suite 2 — RAG API /ask edge cases

**Файл:** `rag-api/tests/test_api.py` (расширить).

### T2.1 /ask с question="привет" возвращает непустой answer

```python
def test_ask_with_short_greeting_returns_non_empty_answer(monkeypatch):
    _patch_runtime_with_empty_retrieval(monkeypatch)
    response = client.post("/ask", json={"question": "привет"})
    assert response.status_code == 200
    body = response.json()
    assert body["answer"], "answer must be non-empty even on refusal"
    assert isinstance(body["sources"], list)
    assert isinstance(body["refused"], bool)
```

**Why:** silence-point S4. Pydantic пропускает `min_length=1`, но если retriever пуст и Mistral отключён, есть риск пустого `build_grounded_answer`. Регрессия гарантирует, что в любом случае API возвращает текст.

### T2.2 /ask с question="/start" возвращает refusal с непустым текстом

```python
def test_ask_with_slash_start_returns_refusal_text(monkeypatch):
    _patch_runtime_with_empty_retrieval(monkeypatch)
    response = client.post("/ask", json={"question": "/start"})
    body = response.json()
    assert body["refused"] is True
    assert "источников" in body["answer"].lower() or "уточните" in body["answer"].lower()
```

**Why:** даже если n8n когда-нибудь обработает `/start` локально, RAG API должен корректно отказывать.

### T2.3 /ask с пустым question возвращает 422

```python
def test_ask_with_empty_question_returns_422():
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 422  # pydantic Field(min_length=1)
```

**Why:** sanity baseline. Защищает от случайного удаления `min_length=1`.

### T2.4 /ask с только-whitespace возвращает 422 или refusal

```python
def test_ask_with_whitespace_question_handled_gracefully():
    response = client.post("/ask", json={"question": "   "})
    # Acceptable: 422 (если добавлен strip-validator) или 200 с refused=true
    assert response.status_code in (200, 422)
    if response.status_code == 200:
        body = response.json()
        assert body["refused"] is True
        assert body["answer"]
```

**Why:** edge case для empty-after-strip; защищает от silence S4.

### T2.5 /ask response всегда содержит `request_log_id` (когда postgres on)

```python
def test_ask_always_logs_request(monkeypatch):
    _patch_runtime_with_postgres(monkeypatch)
    response = client.post("/ask", json={"question": "привет"})
    assert response.status_code == 200
    assert response.json()["request_log_id"] is not None
```

**Why:** Codex предупреждение из R9 (refusal не пишется в request_logs). Регрессия гарантирует логирование на refusal-пути.

---

## Test suite 3 — Greeting/routing contract (после impl `opus_result_followup_greeting_contract.md`)

**Файл:** новый `rag-api/tests/test_greeting_classifier.py` ИЛИ часть `test_n8n_workflow.py`. Зависит от того, где Codex положит классификатор.

Если классификатор на n8n стороне (внутри Whitelist Code node) — тестировать только через workflow JSON regex / схему. Если переедет в Python (`rag-api/app/`) — обычные unit tests.

### T3.1 greeting классифицирует точные приветствия

```python
GREETING_CASES = [
    ("привет", "greeting"),
    ("Привет!", "greeting"),
    ("здравствуйте", "greeting"),
    ("hello", "greeting"),
    ("/start", "greeting"),
    ("/help", "greeting"),
]

@pytest.mark.parametrize("text,expected_route", GREETING_CASES)
def test_classifier_routes_greeting(text, expected_route):
    assert classify_text(text) == expected_route
```

### T3.2 question с приветствием в начале НЕ классифицируется как greeting

```python
def test_classifier_does_not_match_greeting_inside_question():
    assert classify_text("привет можешь рассказать про отпуск") == "question"
```

**Why:** EC1 из greeting_contract.

### T3.3 empty / whitespace классифицируется как empty

```python
@pytest.mark.parametrize("text", ["", "   ", "\t\n"])
def test_classifier_routes_empty(text):
    assert classify_text(text) == "empty"
```

### T3.4 thanks классифицируется отдельно

```python
@pytest.mark.parametrize("text", ["спасибо", "Спасибо!", "thanks"])
def test_classifier_routes_thanks(text):
    assert classify_text(text) == "thanks"
```

### T3.5 off-topic small-talk классифицируется отдельно

```python
@pytest.mark.parametrize("text", ["как дела", "что нового", "что умеешь"])
def test_classifier_routes_offtopic(text):
    assert classify_text(text) == "offtopic"
```

### T3.6 Обычный вопрос классифицируется как question

```python
def test_classifier_routes_question():
    assert classify_text("Сколько длится испытательный срок?") == "question"
    assert classify_text("Какие документы нужны для приёма?") == "question"
```

---

## Test suite 4 — n8n workflow expression syntax sanity

**Файл:** `rag-api/tests/test_n8n_workflow.py` (продолжить).

### T4.1 chat_id в Send Answer и Send Feedback Ack приходит из Format-node, не из expressions с null

```python
def test_send_nodes_have_well_formed_chat_id_expression():
    workflow = _load_workflow()
    nodes = {n["name"]: n for n in workflow["nodes"]}
    for name in ("Send Answer", "Send Feedback Ack", "Send Denied"):
        chat = nodes[name]["parameters"]["chatId"]
        # Expected: ={{ $json.chat_id }} — берёт из output предыдущего node
        assert chat.strip() == "={{ $json.chat_id }}", (
            f"{name} chatId must be ={{ $json.chat_id }} (from previous node), "
            f"got: {chat}"
        )
```

**Why:** защита от регрессии в S2 (если кто-то поменяет на `$node['Whitelist']`).

### T4.2 text expression не использует пустой fallback в Send nodes

```python
def test_send_nodes_have_text_expression_from_json():
    workflow = _load_workflow()
    nodes = {n["name"]: n for n in workflow["nodes"]}
    for name in ("Send Answer", "Send Feedback Ack", "Send Denied"):
        text = nodes[name]["parameters"]["text"]
        assert text.strip() == "={{ $json.text }}", (
            f"{name} text must be ={{ $json.text }}, got: {text}"
        )
```

**Why:** обеспечить, что Send-узлы берут готовый text, а не пытаются собрать его inline (там, где может быть ошибка).

---

## Test suite 5 — Integration / contract (если есть test container or staging API)

**Файл:** новый `rag-api/tests/test_telegram_integration.py`. Требует моков для Telegram API; не запускает live.

### T5.1 Симуляция: greeting message не доходит до /ask

```python
def test_greeting_does_not_call_rag_api(mock_n8n_session):
    # mock Telegram event для "привет" от авторизованного user
    event = make_message_event(user_id=ALLOWED_TEST_ID, text="привет")
    mock_n8n_session.post_webhook(event)
    # /ask НЕ должен быть вызван — request_logs не растёт
    assert mock_n8n_session.rag_api_calls == 0
    # Telegram sendMessage вызывается с greeting текстом
    sent = mock_n8n_session.telegram_messages[-1]
    assert "Здравствуйте" in sent["text"]
```

### T5.2 Симуляция: domain вопрос вызывает /ask

```python
def test_domain_question_calls_rag_api(mock_n8n_session):
    event = make_message_event(user_id=ALLOWED_TEST_ID,
                                text="Сколько длится испытательный срок?")
    mock_n8n_session.post_webhook(event)
    assert mock_n8n_session.rag_api_calls == 1
    sent = mock_n8n_session.telegram_messages[-1]
    assert "Confidence" in sent["text"] or "источник" in sent["text"].lower()
```

### T5.3 Симуляция: unauthorized user получает denial

```python
def test_unauthorized_user_gets_denial(mock_n8n_session):
    event = make_message_event(user_id=999999, text="привет")
    mock_n8n_session.post_webhook(event)
    sent = mock_n8n_session.telegram_messages[-1]
    assert "Доступ запрещен" in sent["text"]
    assert mock_n8n_session.rag_api_calls == 0
```

### T5.4 Симуляция: feedback callback пишет /feedback

```python
def test_feedback_callback_calls_feedback_endpoint(mock_n8n_session):
    event = make_callback_event(user_id=ALLOWED_TEST_ID,
                                 data="feedback:good:request-log-uuid")
    mock_n8n_session.post_webhook(event)
    assert mock_n8n_session.feedback_calls == 1
    sent = mock_n8n_session.telegram_messages[-1]
    assert sent["text"] == "Оценка принята."
```

**Why:** покрытие all four entry-points end-to-end без живого Telegram. Codex может реализовать через `respx` / `responses` библиотеку для mock HTTP.

---

## Fixtures для Codex

### fixtures/telegram_events.py

```python
def make_message_event(user_id: int, text: str, chat_id: int | None = None) -> dict:
    chat_id = chat_id or user_id
    return {
        "update_id": 1,
        "message": {
            "message_id": 1,
            "from": {"id": user_id, "is_bot": False, "first_name": "Test"},
            "chat": {"id": chat_id, "type": "private"},
            "date": 1747000000,
            "text": text,
        },
    }

def make_callback_event(user_id: int, data: str, chat_id: int | None = None) -> dict:
    chat_id = chat_id or user_id
    return {
        "update_id": 2,
        "callback_query": {
            "id": "cb-1",
            "from": {"id": user_id, "is_bot": False, "first_name": "Test"},
            "message": {
                "message_id": 2,
                "from": {"id": 12345, "is_bot": True, "first_name": "TestBot"},
                "chat": {"id": chat_id, "type": "private"},
                "date": 1747000000,
                "text": "previous answer",
            },
            "data": data,
        },
    }
```

### fixtures/rag_runtime.py

Codex уже использует `monkeypatch` для `get_runtime` в `test_api.py`. Расширить existing pattern: `_patch_runtime_with_empty_retrieval`, `_patch_runtime_with_postgres`.

---

## Prioritization для Codex

| Приоритет | Test ID | Зачем | Время |
|-----------|---------|-------|-------|
| **CRITICAL** | T1.1 + T1.2 + T1.3 | Защита от silence (IF schema, inline kb, legacy $node) | 30 мин |
| **CRITICAL** | T2.1 + T2.3 | API edge case на short greeting | 15 мин |
| HIGH | T1.4 + T1.5 + T1.6 + T1.7 | Workflow structural sanity | 15 мин |
| HIGH | T4.1 + T4.2 | Expression syntax | 10 мин |
| MEDIUM | T3.* | Greeting classifier (требует impl) | 30 мин impl + 20 мин tests |
| MEDIUM | T2.2 + T2.4 + T2.5 | API additional edges | 20 мин |
| LOW | T5.* | End-to-end mock | 1 час (требует respx/responses) |

**Минимум для закрытия инцидента «привет → silence»:**
- T1.1, T1.2, T1.3 (workflow JSON корректен)
- T2.1 (API возвращает непустой ответ)
- (Если greeting classifier добавлен) T3.1 + T3.2

Все остальные — defence in depth.

---

## CI integration

После добавления:

```bash
python -m pytest rag-api/tests/ -p no:schemathesis -v
```

Current expected baseline: `python -m pytest -p no:schemathesis` -> `25 passed`.

Если T1.1 после add упадёт — это означает регрессию схемы workflow JSON; Codex должен обновить JSON, не тест.

---

## Что НЕ требуется реализовывать

- Live Telegram E2E — out of scope, Telegram API rate-limit.
- n8n executions UI scrape — слишком хрупко.
- Тесты на cloudflared tunnel — инфраструктура, не код.
- Тесты на Mistral реальные вызовы — патчатся через monkeypatch как в существующих.

## Verification (self-check)

- 5 test suites, 25+ конкретных тест-кейсов с готовым кодом.
- Каждый кейс связан с silence-point из `opus_result_followup_silent_bot_checklist.md`.
- Critical path для закрытия инцидента указан: T1.1–T1.3 + T2.1 минимум.
- Тестовые файлы (`test_n8n_workflow.py`, `test_api.py`) **не редактировались** — только spec.
- Codex может реализовать поэтапно по priority table.
- Все тесты совместимы с существующей структурой (`monkeypatch`, `client`, `_load_workflow`).
- Никакие проектные файлы не редактировались.
