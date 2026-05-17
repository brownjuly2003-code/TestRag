"""Sprint 6 #1: Python-port n8n Whitelist Code → POST /tg/classify.

Покрывает все ветки оригинального JS: feedback variants, followup, greeting,
help/clear/history/docs, normalization (ё/трейлинг-пунктуация), whitelist
allow/deny, empty whitelist, callback_query message_id propagation.
"""
from __future__ import annotations

import pytest

from app import tg_classifier as classifier_mod
from app import tg_copy as copy_mod


ALLOWED = ["42"]


def _msg(text: str, user_id: int = 42, chat_id: int = 100, message_id: int = 1) -> dict:
    return {
        "message": {
            "text": text,
            "chat": {"id": chat_id},
            "from": {"id": user_id},
            "message_id": message_id,
        }
    }


def _cb(data: str, user_id: int = 42, chat_id: int = 100, msg_id: int = 5) -> dict:
    return {
        "callback_query": {
            "data": data,
            "from": {"id": user_id},
            "message": {"chat": {"id": chat_id}, "message_id": msg_id},
        }
    }


# ---------- Authorization ----------


def test_unauthorized_user_gets_denied():
    out = classifier_mod.classify(_msg("Что такое controlled zone?", user_id=999), ALLOWED)
    assert out["authorized"] is False
    assert "999" in out["text"]


def test_empty_whitelist_returns_setup_hint():
    out = classifier_mod.classify(_msg("hi", user_id=42), [])
    assert out["authorized"] is False
    assert "Whitelist не настроен" in out["text"]


def test_authorized_user_passes():
    out = classifier_mod.classify(_msg("Что такое controlled zone?"), ALLOWED)
    assert out["authorized"] is True
    assert out["event_type"] == "question"
    assert out["chat_id"] == 100
    assert out["user_id"] == "42"


# ---------- Direct replies ----------


@pytest.mark.parametrize(
    "raw",
    ["привет", "Привет!", "ПРИВЕТ.", "здравствуйте", "Добрый день,", "hello", "/start"],
)
def test_greeting_routes_to_direct_reply_with_greeting_copy(raw: str):
    out = classifier_mod.classify(_msg(raw), ALLOWED)
    assert out["authorized"] is True
    assert out["event_type"] == "direct_reply"
    assert out["text"] == copy_mod.GREETING_TEXT


@pytest.mark.parametrize("raw", ["спасибо", "Благодарю!"])
def test_thanks_routes_to_direct_reply_thanks(raw: str):
    out = classifier_mod.classify(_msg(raw), ALLOWED)
    assert out["event_type"] == "direct_reply"
    assert out["text"] == copy_mod.THANKS_TEXT


def test_help_routes_to_help_copy():
    out = classifier_mod.classify(_msg("/help"), ALLOWED)
    assert out["event_type"] == "direct_reply"
    assert out["text"] == copy_mod.HELP_TEXT


def test_clear_routes_to_clear_copy():
    out = classifier_mod.classify(_msg("/clear"), ALLOWED)
    assert out["event_type"] == "direct_reply"
    assert out["text"] == copy_mod.CLEAR_TEXT


def test_history_routes_to_history_request():
    out = classifier_mod.classify(_msg("/history"), ALLOWED)
    assert out["event_type"] == "history_request"
    assert out["text"] == "/history"


def test_docs_routes_to_docs_request():
    out = classifier_mod.classify(_msg("/docs"), ALLOWED)
    assert out["event_type"] == "docs_request"
    assert out["text"] == "/docs"


def test_empty_text_returns_empty_input_copy():
    out = classifier_mod.classify(_msg(""), ALLOWED)
    assert out["event_type"] == "direct_reply"
    assert out["text"] == copy_mod.EMPTY_INPUT_TEXT


# ---------- Feedback callbacks ----------


def test_feedback_good():
    out = classifier_mod.classify(_cb("feedback:good:abc-123"), ALLOWED)
    assert out["event_type"] == "feedback"
    assert out["rating"] == "good"
    assert out["request_log_id"] == "abc-123"
    assert out["category"] is None


def test_feedback_bad_clarify_no_rating_yet():
    out = classifier_mod.classify(_cb("feedback:bad:abc-123"), ALLOWED)
    assert out["event_type"] == "feedback_bad_clarify"
    assert out["rating"] is None
    assert out["request_log_id"] == "abc-123"


@pytest.mark.parametrize("reason", ["inaccurate", "outdated", "human"])
def test_feedback_bad_with_reason(reason: str):
    out = classifier_mod.classify(_cb(f"feedback:bad_{reason}:abc-123"), ALLOWED)
    assert out["event_type"] == "feedback"
    assert out["rating"] == "bad"
    assert out["category"] == reason


def test_feedback_bad_unknown_reason_fallback():
    out = classifier_mod.classify(_cb("feedback:bad_unknown:abc"), ALLOWED)
    assert out["event_type"] == "direct_reply"
    assert out["text"] == copy_mod.UNKNOWN_FEEDBACK_REASON_TEXT


def test_feedback_unknown_verb_fallback():
    out = classifier_mod.classify(_cb("feedback:weird:abc"), ALLOWED)
    assert out["event_type"] == "direct_reply"
    assert out["text"] == copy_mod.UNKNOWN_FEEDBACK_TEXT


# ---------- Follow-up callbacks ----------


def test_followup_valid():
    out = classifier_mod.classify(_cb("followup:2:rl-uuid"), ALLOWED)
    assert out["event_type"] == "followup_request"
    assert out["followup_idx"] == 2
    assert out["request_log_id"] == "rl-uuid"


def test_followup_negative_idx_fallback():
    out = classifier_mod.classify(_cb("followup:-1:rl-uuid"), ALLOWED)
    assert out["event_type"] == "direct_reply"
    assert out["text"] == copy_mod.UNRECOGNIZED_FOLLOWUP_TEXT


def test_followup_non_numeric_idx_fallback():
    out = classifier_mod.classify(_cb("followup:abc:rl-uuid"), ALLOWED)
    assert out["event_type"] == "direct_reply"
    assert out["text"] == copy_mod.UNRECOGNIZED_FOLLOWUP_TEXT


def test_followup_missing_request_log_id_fallback():
    # callback split 'followup::rl-id' = 3 parts but parts[1] empty → idx fallback to None
    out = classifier_mod.classify(_cb("followup::rl-uuid"), ALLOWED)
    assert out["event_type"] == "direct_reply"


# ---------- Message-id propagation ----------


def test_user_message_id_from_message():
    out = classifier_mod.classify(_msg("controlled zone", message_id=1001), ALLOWED)
    assert out["user_message_id"] == 1001
    assert out["message_id"] is None  # not from callback


def test_message_id_from_callback_query():
    out = classifier_mod.classify(_cb("feedback:good:abc", msg_id=2222), ALLOWED)
    assert out["message_id"] == 2222
    assert out["user_message_id"] == 2222


# ---------- Normalization parity ----------


def test_normalize_strips_trailing_punctuation_and_yo():
    assert classifier_mod._normalize("ПривЁт!!!") == "привет"
    assert classifier_mod._normalize("  /HELP. ") == "/help"
    assert classifier_mod._normalize("спасибо?") == "спасибо"


def test_parse_allowed_ids_handles_whitespace():
    assert classifier_mod.parse_allowed_ids(" 42 , 100 , ") == ["42", "100"]
    assert classifier_mod.parse_allowed_ids("") == []
    assert classifier_mod.parse_allowed_ids(None) == []  # type: ignore[arg-type]
