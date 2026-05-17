"""Integration tests for tg_poll_bridge.

Mocks `urllib.request.urlopen` (both TG and n8n) — exercises:
- `forward()` success/failure return contract
- offset advance ONLY on successful forward
- offset persistence across `_load_offset`/`_save_offset`
- token redaction in error messages
- `maybe_delete_tg_webhook` skip when env=false / when webhook already empty
"""
from __future__ import annotations

import importlib
import io
import json
import os
import pathlib
import sys
from typing import Any
from unittest import mock

import pytest


TEST_TOKEN = "1234567890:TESTTOKENABCDEF"


@pytest.fixture
def bridge(monkeypatch, tmp_path):
    """Reload main.py under controlled env (token, ephemeral offset path)."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", TEST_TOKEN)
    monkeypatch.setenv("OFFSET_STATE_PATH", str(tmp_path / "offset.txt"))
    monkeypatch.setenv("DELETE_WEBHOOK_ON_START", "true")
    monkeypatch.setenv("N8N_INTERNAL_WEBHOOK", "http://n8n.test/webhook/tg-poll")

    # Сбросить ранее импортированный модуль чтобы env-bound globals перечитались.
    sys.modules.pop("main", None)
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    module = importlib.import_module("main")
    yield module
    sys.modules.pop("main", None)


def _fake_response(payload: dict) -> mock.MagicMock:
    resp = mock.MagicMock()
    resp.read.return_value = json.dumps(payload).encode("utf-8")
    resp.__enter__ = lambda self: self
    resp.__exit__ = lambda *_: False
    return resp


class _HTTPErrorLike(Exception):
    """Mimics urllib.error.HTTPError для тестов forward()."""

    def __init__(self, code: int):
        super().__init__(f"http {code}")
        self.code = code


def test_redact_replaces_token_in_url(bridge):
    leaky = f"https://api.telegram.org/bot{TEST_TOKEN}/getUpdates"
    redacted = bridge._redact(leaky)
    assert TEST_TOKEN not in redacted
    assert "<TG_TOKEN>" in redacted


def test_redact_passes_through_safe_text(bridge):
    assert bridge._redact("connection refused") == "connection refused"


def test_forward_returns_true_on_2xx(bridge, monkeypatch):
    calls: list[tuple[str, Any]] = []

    def fake_urlopen(req, timeout=None):
        calls.append((req.get_method(), req.full_url))
        return _fake_response({"ok": True})

    monkeypatch.setattr(bridge.urllib.request, "urlopen", fake_urlopen)
    ok = bridge.forward({"update_id": 42, "message": {"text": "hi"}})
    assert ok is True
    assert calls and calls[0][0] == "POST"


def test_forward_returns_false_on_http_error(bridge, monkeypatch):
    import urllib.error

    def fake_urlopen(req, timeout=None):
        raise urllib.error.HTTPError(req.full_url, 500, "boom", {}, io.BytesIO(b""))

    monkeypatch.setattr(bridge.urllib.request, "urlopen", fake_urlopen)
    ok = bridge.forward({"update_id": 7})
    assert ok is False


def test_forward_returns_false_on_generic_exception(bridge, monkeypatch):
    def fake_urlopen(req, timeout=None):
        raise ConnectionRefusedError("nope")

    monkeypatch.setattr(bridge.urllib.request, "urlopen", fake_urlopen)
    ok = bridge.forward({"update_id": 8})
    assert ok is False


def test_offset_persistence_roundtrip(bridge):
    bridge._save_offset(123)
    assert bridge._load_offset() == 123


def test_offset_load_returns_zero_when_missing(bridge, tmp_path, monkeypatch):
    # Repoint to a path that doesn't exist
    monkeypatch.setattr(bridge, "OFFSET_STATE_PATH", tmp_path / "missing.txt")
    assert bridge._load_offset() == 0


def test_offset_load_handles_corrupt_state(bridge):
    bridge.OFFSET_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    bridge.OFFSET_STATE_PATH.write_text("not-a-number", encoding="utf-8")
    assert bridge._load_offset() == 0


def test_maybe_delete_webhook_skips_when_disabled(bridge, monkeypatch):
    called: list[str] = []

    monkeypatch.setattr(bridge, "DELETE_WEBHOOK_ON_START", False)
    monkeypatch.setattr(
        bridge.urllib.request,
        "urlopen",
        lambda req, timeout=None: called.append(req.full_url) or _fake_response({}),
    )
    bridge.maybe_delete_tg_webhook()
    assert called == []  # никаких сетевых вызовов


def test_maybe_delete_webhook_skips_when_already_empty(bridge, monkeypatch):
    called: list[str] = []

    def fake_urlopen(req, timeout=None):
        called.append(req.full_url)
        # getWebhookInfo returns empty url → bridge skips deleteWebhook
        if "getWebhookInfo" in req.full_url:
            return _fake_response({"ok": True, "result": {"url": ""}})
        raise AssertionError(f"unexpected call: {req.full_url}")

    monkeypatch.setattr(bridge.urllib.request, "urlopen", fake_urlopen)
    bridge.maybe_delete_tg_webhook()
    assert len(called) == 1
    assert "getWebhookInfo" in called[0]


def test_maybe_delete_webhook_calls_delete_when_set(bridge, monkeypatch):
    called: list[str] = []

    def fake_urlopen(req, timeout=None):
        called.append(req.full_url)
        if "getWebhookInfo" in req.full_url:
            return _fake_response(
                {"ok": True, "result": {"url": "https://other-project.example/hook"}}
            )
        if "deleteWebhook" in req.full_url:
            return _fake_response({"ok": True, "result": True})
        raise AssertionError(f"unexpected: {req.full_url}")

    monkeypatch.setattr(bridge.urllib.request, "urlopen", fake_urlopen)
    bridge.maybe_delete_tg_webhook()
    assert any("getWebhookInfo" in c for c in called)
    assert any("deleteWebhook" in c for c in called)


class _PollLoopExit(BaseException):
    """Sentinel чтобы выйти из бесконечного poll_loop в тесте."""


def test_poll_loop_advances_offset_only_on_successful_forward(bridge, monkeypatch):
    """Critical at-least-once test: при forward fail offset НЕ advance,
    тот же update_id появится в следующем getUpdates."""
    forwarded: list[int] = []
    saved_offsets: list[int] = []

    forward_results = [False, True, True]  # первый fail, потом успех

    def fake_forward(update):
        ok = forward_results.pop(0)
        if ok:
            forwarded.append(update["update_id"])
        return ok

    def fake_save_offset(offset):
        saved_offsets.append(offset)

    monkeypatch.setattr(bridge, "forward", fake_forward)
    monkeypatch.setattr(bridge, "_save_offset", fake_save_offset)
    monkeypatch.setattr(bridge, "_load_offset", lambda: 0)
    monkeypatch.setattr(bridge.time, "sleep", lambda _: None)

    # Имитируем 2 поллa: первый возвращает 1 update (forward fail),
    # второй — те же 2 updates (TG не получил ack), forward True/True.
    poll_responses = [
        {"ok": True, "result": [{"update_id": 100, "message": {"text": "a"}}]},
        {
            "ok": True,
            "result": [
                {"update_id": 100, "message": {"text": "a"}},
                {"update_id": 101, "message": {"text": "b"}},
            ],
        },
    ]

    def fake_request(url, body=None, params=None, timeout=None):
        if not poll_responses:
            raise _PollLoopExit()
        return poll_responses.pop(0)

    monkeypatch.setattr(bridge, "_request", fake_request)

    with pytest.raises(_PollLoopExit):
        bridge.poll_loop()

    # Update 100 был доставлен один раз (на втором poll), 101 — один раз.
    assert forwarded == [100, 101]
    # Offset advance строго после success: 101, 102.
    assert saved_offsets == [101, 102]
