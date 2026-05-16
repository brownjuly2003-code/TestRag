import json
import subprocess
from pathlib import Path


WORKFLOW_PATH = (
    Path(__file__).resolve().parents[2] / "n8n" / "workflows" / "hr-legal-rag-workflow.json"
)


def _load_workflow() -> dict:
    return json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))


def _load_nodes() -> dict:
    return {node["name"]: node for node in _load_workflow()["nodes"]}


def _run_whitelist(payload: dict) -> dict:
    nodes = _load_nodes()
    whitelist_code = nodes["Whitelist"]["parameters"]["jsCode"]
    script = f"""
const $env = {{ ALLOWED_TELEGRAM_USER_IDS: '42' }};
const $json = {json.dumps(payload)};
const result = new Function('$json', '$env', {json.dumps(whitelist_code)})($json, $env);
console.log(JSON.stringify(result[0].json));
"""
    result = subprocess.run(["node", "-e", script], check=True, text=True, capture_output=True)
    return json.loads(result.stdout)


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
    assert workflow["connections"]["Bad Clarify?"]["main"][1][0]["node"] == "Direct Reply?"
    assert workflow["connections"]["Direct Reply?"]["main"][0][0]["node"] == "Send Direct Reply"
    assert workflow["connections"]["Direct Reply?"]["main"][1][0]["node"] == "Send Typing"
    assert workflow["connections"]["Send Typing"]["main"][0][0]["node"] == "Ask RAG API"


def test_bad_clarify_routes_to_edit_reply_markup():
    workflow = _load_workflow()
    assert workflow["connections"]["Bad Clarify?"]["main"][0][0]["node"] == "Edit Reply Markup"


def test_telegram_send_nodes_disable_n8n_attribution():
    nodes = _load_nodes()
    for node_name in ["Send Answer", "Send Feedback Ack", "Send Denied", "Send Direct Reply"]:
        assert nodes[node_name]["parameters"]["additionalFields"]["appendAttribution"] is False


def test_telegram_send_nodes_use_html_parse_mode():
    nodes = _load_nodes()
    for node_name in ["Send Answer", "Send Feedback Ack", "Send Denied", "Send Direct Reply"]:
        assert nodes[node_name]["parameters"]["additionalFields"]["parse_mode"] == "HTML"


def test_send_answer_has_two_feedback_buttons():
    nodes = _load_nodes()
    buttons = nodes["Send Answer"]["parameters"]["inlineKeyboard"]["rows"][0]["row"]["buttons"]
    assert len(buttons) == 2
    labels = [b["text"] for b in buttons]
    assert labels == ["👍 Полезно", "👎 Неточно"]
    assert all("sources" not in b["additionalFields"]["callback_data"] for b in buttons)


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
