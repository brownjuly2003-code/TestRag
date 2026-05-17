"""Sprint 6 #2: OpenAPI contract gate.

Failure означает что Pydantic-модели в `rag-api/app/main.py` разошлись с
закоммиченным `docs/openapi.yaml`. Fix: запустить `python scripts/export_openapi.py`
и закоммитить обновлённый файл вместе с code change.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from app.main import app


REPO_ROOT = Path(__file__).resolve().parents[2]
OPENAPI_YAML = REPO_ROOT / "docs" / "openapi.yaml"


def test_openapi_yaml_committed_matches_app_schema():
    assert OPENAPI_YAML.exists(), (
        f"{OPENAPI_YAML} missing — run `python scripts/export_openapi.py`"
    )
    committed = yaml.safe_load(OPENAPI_YAML.read_text(encoding="utf-8"))
    live = json.loads(json.dumps(app.openapi()))
    assert committed == live, (
        "OpenAPI schema drift detected. Re-export: "
        "`python scripts/export_openapi.py` и commit обновлённый docs/openapi.yaml."
    )


def test_openapi_required_paths_present():
    schema = app.openapi()
    paths = set(schema.get("paths", {}).keys())
    # Core контракт — эти endpoints используются n8n workflow + smoke-скриптами.
    required = {
        "/health",
        "/ask",
        "/feedback",
        "/history",
        "/followup",
        "/docs/summary",
        "/metrics",
        # Sprint 6 #1: n8n routing → rag-api
        "/tg/classify",
        "/tg/copy/{key}",
    }
    missing = required - paths
    assert not missing, f"Missing required paths: {missing}"


def test_openapi_ask_has_debug_field():
    """Sprint 6 #3: explainability должен оставаться в контракте, не быть откатан."""
    schema = app.openapi()
    ask_response = schema["components"]["schemas"]["AskResponse"]["properties"]
    assert "debug" in ask_response


def test_openapi_ask_request_has_debug_param():
    schema = app.openapi()
    ask_request = schema["components"]["schemas"]["AskRequest"]["properties"]
    assert "debug" in ask_request
