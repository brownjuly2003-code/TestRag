import json
import subprocess
from pathlib import Path

from app.tg_classifier import classify as _classify_update


WORKFLOW_PATH = (
    Path(__file__).resolve().parents[2] / "n8n" / "workflows" / "hr-legal-rag-workflow.json"
)


def _load_workflow() -> dict:
    return json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))


def _load_nodes() -> dict:
    return {node["name"]: node for node in _load_workflow()["nodes"]}


def _run_whitelist(payload: dict) -> dict:
    """Sprint 6 #1: Whitelist node — тонкий HTTP-прокси на /tg/classify.
    Тестируем напрямую Python-реализацию (parity guaranteed: одна функция)."""
    return _classify_update(payload, ["42"])


def _run_format_answer(payload: dict, chat_id: int = 42) -> dict:
    nodes = _load_nodes()
    code = nodes["Format Answer"]["parameters"]["jsCode"]
    script = f"""
const $node = {{ Whitelist: {{ json: {{ chat_id: {chat_id} }} }} }};
const $json = {json.dumps(payload)};
const result = new Function('$json', '$node', {json.dumps(code)})($json, $node);
console.log(JSON.stringify(result[0].json));
"""
    result = subprocess.run(["node", "-e", script], check=True, text=True, capture_output=True)
    return json.loads(result.stdout)


def test_if_nodes_use_n8n_v2_filter_conditions():
    nodes = _load_nodes()
    authorized_conditions = nodes["Authorized?"]["parameters"]["conditions"]
    feedback_conditions = nodes["Feedback?"]["parameters"]["conditions"]

    assert authorized_conditions["combinator"] == "and"
    assert authorized_conditions["conditions"] == [
        {
            "leftValue": "={{ String($json.authorized) }}",
            "rightValue": "true",
            "operator": {"type": "string", "operation": "equals"},
        }
    ]

    assert feedback_conditions["combinator"] == "and"
    assert feedback_conditions["conditions"] == [
        {
            "leftValue": "={{ $json.event_type }}",
            "rightValue": "feedback",
            "operator": {"type": "string", "operation": "equals"},
        }
    ]


def test_greeting_is_direct_reply_and_not_rag_question():
    body = _run_whitelist({"message": {"text": "привет", "chat": {"id": 42}, "from": {"id": 42}}})
    assert body["authorized"] is True
    assert body["event_type"] == "direct_reply"
    assert "RAG-ассистент" in body["text"]
    assert "Confidence" not in body["text"]


def test_domain_question_stays_rag_question():
    body = _run_whitelist(
        {
            "message": {
                "text": "Можно ли продлить испытательный срок работнику?",
                "chat": {"id": 42},
                "from": {"id": 42},
            }
        }
    )
    assert body["authorized"] is True
    assert body["event_type"] == "question"
    assert body["text"] == "Можно ли продлить испытательный срок работнику?"


def test_good_feedback_callback_logs_feedback():
    body = _run_whitelist(
        {
            "callback_query": {
                "data": "feedback:good:request-1",
                "from": {"id": 42},
                "message": {"chat": {"id": 42}, "message_id": 7},
            }
        }
    )
    assert body["authorized"] is True
    assert body["event_type"] == "feedback"
    assert body["rating"] == "good"
    assert body["request_log_id"] == "request-1"
    assert body["category"] is None


def test_bad_feedback_callback_drills_down_to_reasons():
    body = _run_whitelist(
        {
            "callback_query": {
                "data": "feedback:bad:request-1",
                "from": {"id": 42},
                "message": {"chat": {"id": 42}, "message_id": 7},
            }
        }
    )
    assert body["authorized"] is True
    assert body["event_type"] == "feedback_bad_clarify"
    assert body["rating"] is None
    assert body["message_id"] == 7
    assert body["request_log_id"] == "request-1"


def test_bad_reason_callback_logs_feedback_with_category():
    body = _run_whitelist(
        {
            "callback_query": {
                "data": "feedback:bad_inaccurate:request-1",
                "from": {"id": 42},
                "message": {"chat": {"id": 42}, "message_id": 7},
            }
        }
    )
    assert body["authorized"] is True
    assert body["event_type"] == "feedback"
    assert body["rating"] == "bad"
    assert body["category"] == "inaccurate"
    assert body["request_log_id"] == "request-1"


def test_unknown_bad_reason_falls_back_to_direct_reply():
    body = _run_whitelist(
        {
            "callback_query": {
                "data": "feedback:bad_lol:request-1",
                "from": {"id": 42},
                "message": {"chat": {"id": 42}, "message_id": 7},
            }
        }
    )
    assert body["authorized"] is True
    assert body["event_type"] == "direct_reply"
    assert body["rating"] is None
    assert "Неизвестная причина" in body["text"]


def test_direct_reply_routes_without_rag_call():
    workflow = _load_workflow()
    assert workflow["connections"]["Feedback?"]["main"][1][0]["node"] == "Bad Clarify?"
    # Bad Clarify? no → Followup? → (no) → Direct Reply?
    assert workflow["connections"]["Bad Clarify?"]["main"][1][0]["node"] == "Followup?"
    assert workflow["connections"]["Followup?"]["main"][1][0]["node"] == "Direct Reply?"
    assert workflow["connections"]["Direct Reply?"]["main"][0][0]["node"] == "Send Direct Reply"
    assert workflow["connections"]["Direct Reply?"]["main"][1][0]["node"] == "History?"
    assert workflow["connections"]["Docs?"]["main"][1][0]["node"] == "Send Typing"
    assert workflow["connections"]["Send Typing"]["main"][0][0]["node"] == "Ask RAG API"


def test_bad_clarify_routes_to_edit_reply_markup():
    workflow = _load_workflow()
    assert workflow["connections"]["Bad Clarify?"]["main"][0][0]["node"] == "Edit Reply Markup"


def test_telegram_send_nodes_disable_n8n_attribution():
    nodes = _load_nodes()
    for node_name in ["Send Feedback Ack", "Send Denied", "Send Direct Reply"]:
        assert nodes[node_name]["parameters"]["additionalFields"]["appendAttribution"] is False


def test_telegram_send_nodes_use_html_parse_mode():
    nodes = _load_nodes()
    for node_name in ["Send Feedback Ack", "Send Denied", "Send Direct Reply"]:
        assert nodes[node_name]["parameters"]["additionalFields"]["parse_mode"] == "HTML"


def test_send_answer_is_http_node_with_dynamic_reply_markup():
    """Send Answer теперь HTTP sendMessage: inline_keyboard приходит dynamic из Format Answer."""
    nodes = _load_nodes()
    node = nodes["Send Answer"]
    assert node["type"] == "n8n-nodes-base.httpRequest"
    assert "sendMessage" in node["parameters"]["url"]
    body = node["parameters"]["jsonBody"]
    assert "$json.inline_keyboard" in body
    assert "parse_mode: 'HTML'" in body or 'parse_mode: "HTML"' in body


def test_ask_rag_reads_user_input_from_whitelist_not_send_typing_response():
    """Send Typing — HTTP node, его output затирает $json своим Bot API ответом.
    Ask RAG API не должен брать question/telegram_user_id из $json — иначе /ask отдаст 422."""
    nodes = _load_nodes()
    body = nodes["Ask RAG API"]["parameters"]["jsonBody"]
    assert "$node['Whitelist'].json.text" in body or '$node["Whitelist"].json.text' in body
    assert "$node['Whitelist'].json.user_id" in body or '$node["Whitelist"].json.user_id' in body
    assert "$json.text" not in body, "$json.text после Send Typing = undefined"


def test_send_typing_node_calls_telegram_send_chat_action():
    nodes = _load_nodes()
    node = nodes["Send Typing"]
    assert node["type"] == "n8n-nodes-base.httpRequest"
    assert "sendChatAction" in node["parameters"]["url"]
    assert "typing" in node["parameters"]["jsonBody"]


def test_edit_reply_markup_node_offers_three_reason_buttons():
    nodes = _load_nodes()
    node = nodes["Edit Reply Markup"]
    assert node["type"] == "n8n-nodes-base.httpRequest"
    assert "editMessageReplyMarkup" in node["parameters"]["url"]
    body = node["parameters"]["jsonBody"]
    for verb in ["bad_inaccurate", "bad_outdated", "bad_human"]:
        assert verb in body


def test_send_feedback_passes_category_when_present():
    nodes = _load_nodes()
    body = nodes["Send Feedback"]["parameters"]["jsonBody"]
    assert "$json.category" in body
    assert "category:" in body


def test_format_answer_drops_confidence_in_favor_of_found_summary():
    result = _run_format_answer(
        {
            "answer": "Краткий ответ.",
            "confidence": 0.7,
            "request_log_id": "rl1",
            "sources": [{"file": "01_hr.md", "section": "Раздел 1", "score": 0.85}],
        }
    )
    text = result["text"]
    assert "Confidence" not in text
    assert "Найдено 1 релевантный документ" in text
    assert "<code>01_hr.md</code>" in text


def test_format_answer_handles_plural_documents():
    result = _run_format_answer(
        {
            "answer": "x",
            "request_log_id": "rl",
            "sources": [
                {"file": f"f{i}.md", "section": "s", "score": 0.1} for i in range(3)
            ],
        }
    )
    assert "Найдено 3 релевантных документа" in result["text"]

    result5 = _run_format_answer(
        {
            "answer": "x",
            "request_log_id": "rl",
            "sources": [
                {"file": f"f{i}.md", "section": "s", "score": 0.1} for i in range(5)
            ],
        }
    )
    assert "Найдено 5 релевантных документов" in result5["text"]


def test_format_answer_html_escapes_user_content():
    result = _run_format_answer(
        {
            "answer": "Видел <script>alert(1)</script>",
            "request_log_id": "rl",
            "sources": [],
        }
    )
    text = result["text"]
    assert "<script>" not in text
    assert "&lt;script&gt;" in text


def test_format_answer_converts_markdown_to_html():
    """Mistral возвращает Markdown V1 (**bold**, `code`, - list).
    Format Answer обязан конвертировать перед отдачей в TG (parse_mode=HTML)."""
    result = _run_format_answer(
        {
            "answer": "**Ответ:** это **controlled zone**.\n- AWB\n- ULD\nПример `controlled_zone_access`.",
            "request_log_id": "rl",
            "sources": [],
        }
    )
    text = result["text"]
    assert "<b>Ответ:</b>" in text
    assert "<b>controlled zone</b>" in text
    assert "**" not in text
    assert "<code>controlled_zone_access</code>" in text
    assert "• AWB" in text
    assert "• ULD" in text


def _run_format_answer_all(payload: dict, chat_id: int = 42) -> list[dict]:
    """Format Answer теперь возвращает array of items (split на части)."""
    nodes = _load_nodes()
    code = nodes["Format Answer"]["parameters"]["jsCode"]
    script = f"""
const $node = {{ Whitelist: {{ json: {{ chat_id: {chat_id} }} }} }};
const $json = {json.dumps(payload)};
const result = new Function('$json', '$node', {json.dumps(code)})($json, $node);
console.log(JSON.stringify(result));
"""
    result = subprocess.run(["node", "-e", script], check=True, text=True, capture_output=True)
    return [item["json"] for item in json.loads(result.stdout)]


def test_format_answer_splits_long_response_into_parts_under_tg_max():
    """Telegram sendMessage отбивает text > 4096. Format Answer split на части ≤4000 chars."""
    long_answer = "**Ответ:** " + ("Параграф с инфой про controlled zone и aviation security.\n\n" * 100)
    sources = [
        {"file": f"long_filename_{i:02d}.md", "section": f"Раздел {i}", "score": 0.5}
        for i in range(5)
    ]
    items = _run_format_answer_all({"answer": long_answer, "request_log_id": "rl", "sources": sources})
    assert len(items) > 1, "длинный ответ должен разбиться минимум на 2 части"
    for item in items:
        assert len(item["text"]) <= 4000, f"part too long: {len(item['text'])}"
    assert items[-1]["is_last"] is True
    for it in items[:-1]:
        assert it["is_last"] is False
    # последняя часть должна содержать summary + sources
    assert "Найдено" in items[-1]["text"]
    assert "Источники:" in items[-1]["text"]


def test_format_answer_single_part_when_short():
    items = _run_format_answer_all({
        "answer": "Нормальный ответ на пару предложений.",
        "request_log_id": "rl",
        "sources": [{"file": "a.md", "section": "X", "score": 0.5}],
    })
    assert len(items) == 1
    assert items[0]["is_last"] is True
    assert items[0]["part_total"] == 1
    # короткий ответ — без маркера части
    assert "часть" not in items[0]["text"]


def test_format_answer_part_indicator_visible_on_multipart():
    long_answer = "Параграф.\n\n" * 400  # ~4400 chars → 2 parts
    items = _run_format_answer_all({"answer": long_answer, "request_log_id": "rl", "sources": []})
    assert len(items) >= 2
    for i, it in enumerate(items):
        assert f"часть {i + 1}/{len(items)}" in it["text"]


def test_format_answer_balances_unclosed_html_tags_across_split():
    """Если split разрывает <b>...</b> между частями, оба куска должны быть валидны."""
    # одна огромная фраза в **bold** на ~5000 chars (без \n\n внутри bold)
    bolded = "**" + ("очень длинный жирный текст про controlled zone access procedure. " * 80) + "**"
    items = _run_format_answer_all({"answer": bolded, "request_log_id": "rl", "sources": []})
    if len(items) > 1:
        for it in items:
            opens = it["text"].count("<b>")
            closes = it["text"].count("</b>")
            assert opens == closes, f"unbalanced <b> in part: opens={opens} closes={closes}"


def test_help_command_returns_direct_reply_with_html_help_text():
    body = _run_whitelist({"message": {"text": "/help", "chat": {"id": 42}, "from": {"id": 42}}})
    assert body["event_type"] == "direct_reply"
    assert "<b>" in body["text"]
    assert "/history" in body["text"]
    assert "/docs" in body["text"]


def test_clear_command_returns_direct_reply_with_state_explanation():
    body = _run_whitelist({"message": {"text": "/clear", "chat": {"id": 42}, "from": {"id": 42}}})
    assert body["event_type"] == "direct_reply"
    assert "не сохраняется" in body["text"].lower() or "состояние" in body["text"].lower()


def test_history_command_sets_history_request_event_type():
    body = _run_whitelist({"message": {"text": "/history", "chat": {"id": 42}, "from": {"id": 42}}})
    assert body["event_type"] == "history_request"


def test_docs_command_sets_docs_request_event_type():
    body = _run_whitelist({"message": {"text": "/docs", "chat": {"id": 42}, "from": {"id": 42}}})
    assert body["event_type"] == "docs_request"


def test_workflow_routes_multipart_through_last_part_if():
    """Format Answer выдаёт N items с is_last флагом. Last Part? разделяет:
    last → Send Answer (с keyboard), не last → Send Answer Part (без keyboard)."""
    workflow = _load_workflow()
    nodes = {n["name"]: n for n in workflow["nodes"]}
    assert "Last Part?" in nodes
    assert "Send Answer Part" in nodes
    # Send Answer Part — Telegram-узел БЕЗ inlineKeyboard
    assert "inlineKeyboard" not in nodes["Send Answer Part"]["parameters"]
    assert nodes["Send Answer Part"]["parameters"]["additionalFields"]["parse_mode"] == "HTML"

    assert workflow["connections"]["Format Answer"]["main"][0][0]["node"] == "Last Part?"
    assert workflow["connections"]["Last Part?"]["main"][0][0]["node"] == "Send Answer"
    assert workflow["connections"]["Last Part?"]["main"][1][0]["node"] == "Send Answer Part"


def test_workflow_has_history_and_docs_branches():
    workflow = _load_workflow()
    nodes = {n["name"]: n for n in workflow["nodes"]}
    for required in ["History?", "Docs?", "Fetch History", "Format History", "Fetch Docs", "Format Docs"]:
        assert required in nodes, f"missing {required}"

    assert workflow["connections"]["Direct Reply?"]["main"][1][0]["node"] == "History?"
    assert workflow["connections"]["History?"]["main"][0][0]["node"] == "Fetch History"
    assert workflow["connections"]["History?"]["main"][1][0]["node"] == "Docs?"
    assert workflow["connections"]["Docs?"]["main"][0][0]["node"] == "Fetch Docs"
    assert workflow["connections"]["Docs?"]["main"][1][0]["node"] == "Send Typing"
    assert workflow["connections"]["Format History"]["main"][0][0]["node"] == "Send Direct Reply"
    assert workflow["connections"]["Format Docs"]["main"][0][0]["node"] == "Send Direct Reply"


def test_fetch_history_uses_get_with_whitelist_user_id():
    nodes = _load_nodes()
    node = nodes["Fetch History"]
    assert node["parameters"]["method"] == "GET"
    assert "/history" in node["parameters"]["url"]
    assert "$node['Whitelist'].json.user_id" in node["parameters"]["url"] or '$node["Whitelist"].json.user_id' in node["parameters"]["url"]


def test_fetch_docs_uses_get_summary_endpoint():
    nodes = _load_nodes()
    node = nodes["Fetch Docs"]
    assert node["parameters"]["method"] == "GET"
    assert "/docs/summary" in node["parameters"]["url"]


def test_send_feedback_passes_category_as_dedicated_field():
    nodes = _load_nodes()
    body = nodes["Send Feedback"]["parameters"]["jsonBody"]
    assert "category: $json.category" in body
    assert "telegram_inline_button" in body
    assert "category:" not in body.split("category: $json.category")[0]


def _run_format(node_name: str, payload: dict, chat_id: int = 42) -> dict:
    nodes = _load_nodes()
    code = nodes[node_name]["parameters"]["jsCode"]
    script = f"""
const $node = {{ Whitelist: {{ json: {{ chat_id: {chat_id} }} }} }};
const $json = {json.dumps(payload)};
const result = new Function('$json', '$node', {json.dumps(code)})($json, $node);
console.log(JSON.stringify(result[0].json));
"""
    result = subprocess.run(["node", "-e", script], check=True, text=True, capture_output=True)
    return json.loads(result.stdout)


def test_format_history_renders_items_with_html_and_plural():
    result = _run_format("Format History", {
        "items": [
            {"question": "Что такое controlled zone?", "refused": False, "created_at": "2026-05-17T01:47:00"},
            {"question": "AWB обязателен?", "refused": False, "created_at": "2026-05-17T01:30:00"},
        ],
    })
    text = result["text"]
    assert "Последние 2 запроса" in text
    assert "<code>Что такое controlled zone?</code>" in text


def test_format_history_handles_singular_plural():
    result = _run_format("Format History", {"items": [{"question": "x", "refused": False, "created_at": "2026-05-17T01:00:00"}]})
    assert "Последний 1 запрос" in result["text"]


def test_format_history_handles_empty():
    result = _run_format("Format History", {"items": []})
    assert "пуста" in result["text"]


def test_format_docs_renders_categories_with_total():
    result = _run_format("Format Docs", {
        "categories": [
            {"category": "01_hr_pol", "label": "HR — политики", "doc_count": 60, "sample_files": []},
            {"category": "07_faq", "label": "FAQ", "doc_count": 8, "sample_files": []},
        ],
        "total_docs": 68,
    })
    text = result["text"]
    assert "Корпус знаний: 68 документов" in text
    assert "HR — политики" in text and "(60)" in text
    assert "FAQ" in text and "(8)" in text


def test_format_docs_includes_sample_file_names():
    """BCG polish: на каждой категории показываем 1-2 sample doc названия для конкретики."""
    result = _run_format("Format Docs", {
        "categories": [
            {
                "category": "01_hr_pol",
                "label": "HR — политики",
                "doc_count": 13,
                "sample_files": ["01_hr_pol_safety.md", "01_hr_pol_attendance.md"],
            },
        ],
        "total_docs": 13,
    })
    text = result["text"]
    assert "<code>01_hr_pol_safety.md</code>" in text
    assert "<code>01_hr_pol_attendance.md</code>" in text


def _run_format_feedback(category: str | None, chat_id: int = 42) -> dict:
    nodes = _load_nodes()
    code = nodes["Format Feedback"]["parameters"]["jsCode"]
    script = f"""
const $node = {{ Whitelist: {{ json: {{ chat_id: {chat_id}, category: {json.dumps(category)} }} }} }};
const $json = {{}};
const result = new Function('$json', '$node', {json.dumps(code)})($json, $node);
console.log(JSON.stringify(result[0].json));
"""
    result = subprocess.run(["node", "-e", script], check=True, text=True, capture_output=True)
    return json.loads(result.stdout)


def test_format_feedback_emits_default_text_for_inaccurate_category():
    out = _run_format_feedback("inaccurate")
    assert out["text"] == "Оценка принята."


def test_format_feedback_emits_human_handover_text_for_human_category():
    out = _run_format_feedback("human")
    assert "HR/Legal" in out["text"]
    assert "ручную обработку" in out["text"]


def test_format_feedback_emits_default_text_when_category_missing():
    out = _run_format_feedback(None)
    assert out["text"] == "Оценка принята."


def test_whitelist_captures_user_message_id_from_message():
    body = _run_whitelist({"message": {"text": "Что такое controlled zone?", "chat": {"id": 42}, "from": {"id": 42}, "message_id": 1001}})
    assert body["user_message_id"] == 1001


def test_whitelist_captures_user_message_id_from_callback_query():
    body = _run_whitelist(
        {
            "callback_query": {
                "data": "feedback:good:request-1",
                "from": {"id": 42},
                "message": {"chat": {"id": 42}, "message_id": 777},
            }
        }
    )
    assert body["user_message_id"] == 777


def test_format_answer_first_part_carries_reply_to_message_id():
    nodes = _load_nodes()
    code = nodes["Format Answer"]["parameters"]["jsCode"]
    script = f"""
const $node = {{ Whitelist: {{ json: {{ chat_id: 42, user_message_id: 1234 }} }} }};
const $json = {json.dumps({"answer": "Параграф.\\n\\n" * 400, "request_log_id": "rl-1", "sources": []})};
const result = new Function('$json', '$node', {json.dumps(code)})($json, $node);
console.log(JSON.stringify(result));
"""
    result = subprocess.run(["node", "-e", script], check=True, text=True, capture_output=True)
    items = [item["json"] for item in json.loads(result.stdout)]
    assert len(items) >= 2
    assert items[0]["reply_to_message_id"] == 1234
    for it in items[1:]:
        assert it["reply_to_message_id"] is None


def test_format_answer_single_part_has_reply_to_message_id():
    nodes = _load_nodes()
    code = nodes["Format Answer"]["parameters"]["jsCode"]
    script = f"""
const $node = {{ Whitelist: {{ json: {{ chat_id: 42, user_message_id: 2222 }} }} }};
const $json = {json.dumps({"answer": "Короткий ответ.", "request_log_id": "rl-1", "sources": []})};
const result = new Function('$json', '$node', {json.dumps(code)})($json, $node);
console.log(JSON.stringify(result));
"""
    result = subprocess.run(["node", "-e", script], check=True, text=True, capture_output=True)
    items = [item["json"] for item in json.loads(result.stdout)]
    assert len(items) == 1
    assert items[0]["reply_to_message_id"] == 2222


def test_send_answer_http_body_includes_reply_to_message_id():
    nodes = _load_nodes()
    body = nodes["Send Answer"]["parameters"]["jsonBody"]
    assert "reply_to_message_id: $json.reply_to_message_id" in body


def test_send_answer_part_uses_reply_to_message_id():
    nodes = _load_nodes()
    additional = nodes["Send Answer Part"]["parameters"]["additionalFields"]
    assert "replyToMessageId" in additional
    assert "$json.reply_to_message_id" in additional["replyToMessageId"]


def test_followup_callback_parses_to_followup_request_event():
    body = _run_whitelist(
        {
            "callback_query": {
                "data": "followup:1:6f0e7b1a-0000-0000-0000-000000000abc",
                "from": {"id": 42},
                "message": {"chat": {"id": 42}, "message_id": 17},
            }
        }
    )
    assert body["authorized"] is True
    assert body["event_type"] == "followup_request"
    assert body["followup_idx"] == 1
    assert body["request_log_id"] == "6f0e7b1a-0000-0000-0000-000000000abc"


def test_malformed_followup_callback_falls_back_to_direct_reply():
    body = _run_whitelist(
        {
            "callback_query": {
                "data": "followup:abc:",
                "from": {"id": 42},
                "message": {"chat": {"id": 42}, "message_id": 17},
            }
        }
    )
    assert body["authorized"] is True
    assert body["event_type"] == "direct_reply"
    assert "не удалось" in body["text"].lower() or "вопрос текстом" in body["text"].lower()


def test_workflow_has_followup_branch_nodes():
    workflow = _load_workflow()
    nodes = {n["name"]: n for n in workflow["nodes"]}
    for required in ["Followup?", "Resolve Follow-up", "Send Typing Followup", "Ask RAG Followup"]:
        assert required in nodes, f"missing {required}"


def test_followup_branch_routes_through_resolve_then_typing_then_ask():
    workflow = _load_workflow()
    # Bad Clarify? main[1] (no) теперь → Followup?, не Direct Reply?
    assert workflow["connections"]["Bad Clarify?"]["main"][1][0]["node"] == "Followup?"
    # Followup? yes → Resolve Follow-up
    assert workflow["connections"]["Followup?"]["main"][0][0]["node"] == "Resolve Follow-up"
    # Followup? no → Direct Reply?
    assert workflow["connections"]["Followup?"]["main"][1][0]["node"] == "Direct Reply?"
    # Resolve → Send Typing FU → Ask RAG FU → Format Answer
    assert workflow["connections"]["Resolve Follow-up"]["main"][0][0]["node"] == "Send Typing Followup"
    assert workflow["connections"]["Send Typing Followup"]["main"][0][0]["node"] == "Ask RAG Followup"
    assert workflow["connections"]["Ask RAG Followup"]["main"][0][0]["node"] == "Format Answer"


def test_resolve_followup_node_calls_followup_endpoint_with_whitelist_params():
    nodes = _load_nodes()
    node = nodes["Resolve Follow-up"]
    assert node["type"] == "n8n-nodes-base.httpRequest"
    assert node["parameters"]["method"] == "GET"
    url = node["parameters"]["url"]
    assert "/followup" in url
    assert "$node['Whitelist'].json.request_log_id" in url or '$node["Whitelist"].json.request_log_id' in url
    assert "$node['Whitelist'].json.followup_idx" in url or '$node["Whitelist"].json.followup_idx' in url


def test_ask_rag_followup_reads_question_from_resolve_node():
    """Send Typing Followup затирает $json своим Bot API ответом, поэтому Ask RAG FU
    должен читать question из $node['Resolve Follow-up'].json, не из $json."""
    nodes = _load_nodes()
    body = nodes["Ask RAG Followup"]["parameters"]["jsonBody"]
    assert "$node['Resolve Follow-up'].json.question" in body or '$node["Resolve Follow-up"].json.question' in body
    assert "$node['Whitelist'].json.user_id" in body or '$node["Whitelist"].json.user_id' in body
    assert "$json.question" not in body


def test_format_answer_emits_inline_keyboard_with_followup_and_feedback_buttons_on_last_part():
    items = _run_format_answer_all(
        {
            "answer": "Короткий ответ про controlled zone.",
            "request_log_id": "rl-abc",
            "sources": [
                {"file": "01_hr_pol_safety.md", "section": "Контролируемая зона", "score": 0.92},
                {"file": "06_comp_security.md", "section": "Процедура доступа", "score": 0.81},
                {"file": "07_faq_general.md", "section": "Прочее", "score": 0.4},
            ],
        }
    )
    assert len(items) == 1
    keyboard = items[0]["inline_keyboard"]
    assert keyboard is not None
    rows = keyboard["inline_keyboard"]
    # 2 follow-up + 2 feedback = 2 ряда
    assert len(rows) == 2
    follow_row, fb_row = rows
    assert all(b["callback_data"].startswith("followup:") for b in follow_row)
    assert [b["callback_data"] for b in follow_row] == [
        "followup:0:rl-abc",
        "followup:1:rl-abc",
    ]
    assert all(b["text"].startswith("📎") for b in follow_row)
    assert [b["callback_data"] for b in fb_row] == [
        "feedback:good:rl-abc",
        "feedback:bad:rl-abc",
    ]
    # callback_data ≤ 64 bytes (Telegram limit)
    for row in rows:
        for b in row:
            assert len(b["callback_data"].encode("utf-8")) <= 64


def test_format_answer_omits_followup_row_when_no_sources():
    items = _run_format_answer_all(
        {
            "answer": "Не нашёл подходящих источников.",
            "request_log_id": "rl-empty",
            "sources": [],
        }
    )
    keyboard = items[0]["inline_keyboard"]
    rows = keyboard["inline_keyboard"]
    assert len(rows) == 1  # только feedback row
    assert [b["callback_data"] for b in rows[0]] == [
        "feedback:good:rl-empty",
        "feedback:bad:rl-empty",
    ]


def test_format_answer_non_last_part_has_null_keyboard():
    long_answer = "Параграф.\n\n" * 400  # 2+ parts
    items = _run_format_answer_all(
        {
            "answer": long_answer,
            "request_log_id": "rl-long",
            "sources": [{"file": "a.md", "section": "X", "score": 0.5}],
        }
    )
    assert len(items) >= 2
    for it in items[:-1]:
        assert it["inline_keyboard"] is None
    assert items[-1]["inline_keyboard"] is not None


def test_format_answer_md_conversion_does_not_re_escape_safe_tags():
    """XSS-попытка с MD: <script> должен escape'нуться, но **bold** конвертироваться."""
    result = _run_format_answer(
        {
            "answer": "Видел <script>x</script> + **жирный**",
            "request_log_id": "rl",
            "sources": [],
        }
    )
    text = result["text"]
    assert "&lt;script&gt;" in text
    assert "<b>жирный</b>" in text
    assert "<script>" not in text


def test_format_answer_high_confidence_chip():
    result = _run_format_answer(
        {
            "answer": "Краткий ответ про controlled zone.",
            "confidence": 0.85,
            "request_log_id": "rl",
            "sources": [{"file": "01_hr.md", "section": "X", "score": 0.9}],
        }
    )
    text = result["text"]
    assert "🟢" in text
    assert "Высокая уверенность" in text
    # bare score должен исчезнуть из sources block (anti-pattern)
    assert "score 0.9" not in text


def test_format_answer_medium_confidence_chip():
    result = _run_format_answer(
        {
            "answer": "Ответ.",
            "confidence": 0.55,
            "request_log_id": "rl",
            "sources": [],
        }
    )
    text = result["text"]
    assert "🟡" in text
    assert "Средняя уверенность" in text


def test_format_answer_low_confidence_chip():
    result = _run_format_answer(
        {
            "answer": "Возможно.",
            "confidence": 0.2,
            "request_log_id": "rl",
            "sources": [],
        }
    )
    text = result["text"]
    assert "🟠" in text
    assert "Низкая уверенность" in text


def test_format_answer_refusal_shows_next_steps():
    """API вернул refused=True → блок 'Что делать дальше' + 🧑‍💼 эскалация."""
    result = _run_format_answer(
        {
            "answer": "Данных недостаточно для ответа.",
            "confidence": 0.0,
            "refused": True,
            "request_log_id": "rl",
            "sources": [],
        }
    )
    text = result["text"]
    assert "Что делать дальше" in text
    assert "/docs" in text
    assert "🧑‍💼" in text
    # на refusal chip не показываем (бесполезен)
    assert "Высокая уверенность" not in text
    assert "Средняя уверенность" not in text
    assert "Низкая уверенность" not in text


def test_format_answer_refusal_detection_by_text():
    """Mistral вернул 'Данных недостаточно' но refused=false (LLM не помечает) — детектим по тексту."""
    result = _run_format_answer(
        {
            "answer": "Данных недостаточно для ответа на этот вопрос.",
            "confidence": 0.9,
            "request_log_id": "rl",
            "sources": [{"file": "a.md", "section": "X", "score": 0.5}],
        }
    )
    text = result["text"]
    assert "Что делать дальше" in text
    # на refusal источники называются 'Ближайшие документы' а не 'Источники'
    assert "Ближайшие документы" in text


def test_format_answer_sources_have_no_bare_score():
    """Anti-pattern: bare numeric score в UI. Memory: feedback_concrete_test_questions / BCG-bar."""
    result = _run_format_answer(
        {
            "answer": "Ответ.",
            "confidence": 0.8,
            "request_log_id": "rl",
            "sources": [
                {"file": "f1.md", "section": "S1", "score": 0.91},
                {"file": "f2.md", "section": "S2", "score": 0.74},
            ],
        }
    )
    text = result["text"]
    assert "score 0.91" not in text
    assert "score 0.74" not in text
    assert "0.91" not in text
    assert "0.74" not in text
    # источники остаются с file + section в clean формате
    assert "<code>f1.md</code> — S1" in text
    assert "<code>f2.md</code> — S2" in text
