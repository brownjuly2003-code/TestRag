import json
import subprocess
from pathlib import Path


def test_if_nodes_use_n8n_v2_filter_conditions():
    workflow_path = Path(__file__).resolve().parents[2] / "n8n" / "workflows" / "hr-legal-rag-workflow.json"
    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    nodes = {node["name"]: node for node in workflow["nodes"]}

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
    workflow_path = Path(__file__).resolve().parents[2] / "n8n" / "workflows" / "hr-legal-rag-workflow.json"
    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    nodes = {node["name"]: node for node in workflow["nodes"]}
    whitelist_code = nodes["Whitelist"]["parameters"]["jsCode"]

    script = f"""
const $env = {{ ALLOWED_TELEGRAM_USER_IDS: '42' }};
const $json = {{
  message: {{
    text: 'привет',
    chat: {{ id: 42 }},
    from: {{ id: 42 }}
  }}
}};
const result = new Function('$json', '$env', {json.dumps(whitelist_code)})($json, $env);
console.log(JSON.stringify(result[0].json));
"""
    result = subprocess.run(["node", "-e", script], check=True, text=True, capture_output=True)
    body = json.loads(result.stdout)

    assert body["authorized"] is True
    assert body["event_type"] == "direct_reply"
    assert "RAG-ассистент" in body["text"]
    assert "Confidence" not in body["text"]


def test_domain_question_stays_rag_question():
    workflow_path = Path(__file__).resolve().parents[2] / "n8n" / "workflows" / "hr-legal-rag-workflow.json"
    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    nodes = {node["name"]: node for node in workflow["nodes"]}
    whitelist_code = nodes["Whitelist"]["parameters"]["jsCode"]

    script = f"""
const $env = {{ ALLOWED_TELEGRAM_USER_IDS: '42' }};
const $json = {{
  message: {{
    text: 'Можно ли продлить испытательный срок работнику?',
    chat: {{ id: 42 }},
    from: {{ id: 42 }}
  }}
}};
const result = new Function('$json', '$env', {json.dumps(whitelist_code)})($json, $env);
console.log(JSON.stringify(result[0].json));
"""
    result = subprocess.run(["node", "-e", script], check=True, text=True, capture_output=True)
    body = json.loads(result.stdout)

    assert body["authorized"] is True
    assert body["event_type"] == "question"
    assert body["text"] == "Можно ли продлить испытательный срок работнику?"


def test_feedback_callback_stays_feedback_event():
    workflow_path = Path(__file__).resolve().parents[2] / "n8n" / "workflows" / "hr-legal-rag-workflow.json"
    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    nodes = {node["name"]: node for node in workflow["nodes"]}
    whitelist_code = nodes["Whitelist"]["parameters"]["jsCode"]

    script = f"""
const $env = {{ ALLOWED_TELEGRAM_USER_IDS: '42' }};
const $json = {{
  callback_query: {{
    data: 'feedback:bad:request-1',
    from: {{ id: 42 }},
    message: {{ chat: {{ id: 42 }} }}
  }}
}};
const result = new Function('$json', '$env', {json.dumps(whitelist_code)})($json, $env);
console.log(JSON.stringify(result[0].json));
"""
    result = subprocess.run(["node", "-e", script], check=True, text=True, capture_output=True)
    body = json.loads(result.stdout)

    assert body["authorized"] is True
    assert body["event_type"] == "feedback"
    assert body["rating"] == "bad"
    assert body["request_log_id"] == "request-1"


def test_direct_reply_routes_without_rag_call():
    workflow_path = Path(__file__).resolve().parents[2] / "n8n" / "workflows" / "hr-legal-rag-workflow.json"
    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))

    assert workflow["connections"]["Feedback?"]["main"][1][0]["node"] == "Direct Reply?"
    assert workflow["connections"]["Direct Reply?"]["main"][0][0]["node"] == "Send Direct Reply"
    assert workflow["connections"]["Direct Reply?"]["main"][1][0]["node"] == "Ask RAG API"


def test_telegram_send_nodes_disable_n8n_attribution():
    workflow_path = Path(__file__).resolve().parents[2] / "n8n" / "workflows" / "hr-legal-rag-workflow.json"
    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    nodes = {node["name"]: node for node in workflow["nodes"]}

    for node_name in ["Send Answer", "Send Feedback Ack", "Send Denied", "Send Direct Reply"]:
        assert nodes[node_name]["parameters"]["additionalFields"]["appendAttribution"] is False
