"""Telegram update classifier.

Sprint 6 #1: бизнес-логика whitelist/routing/copy перенесена из
n8n Whitelist Code node в rag-api. Логика в чистой Python-функции,
endpoint POST /tg/classify в main.py делает её доступной для n8n.

После переноса n8n Whitelist node — тонкий HTTP-прокси, что закрывает
Issue #14 (n8n coupling) из kimi_audit и разрешает выставить
N8N_BLOCK_ENV_ACCESS_IN_NODE=true.
"""
from __future__ import annotations

import re
from typing import Any

from . import tg_copy


GREETING_TRIGGERS = frozenset(
    {
        "привет",
        "здравствуйте",
        "добрый день",
        "доброе утро",
        "добрый вечер",
        "hello",
        "hi",
        "/start",
        "start",
    }
)
THANKS_TRIGGERS = frozenset({"спасибо", "благодарю"})
REASON_KEYS = frozenset({"inaccurate", "outdated", "human"})

_TRAILING_PUNCT_RE = re.compile(r"[.!?,]+$")


def _normalize(text: str) -> str:
    """JS-parity: trim → lower → ё→е → strip trailing .!?,"""
    stripped = text.strip().lower().replace("ё", "е")
    return _TRAILING_PUNCT_RE.sub("", stripped)


def _safe_int(value: str) -> int | None:
    try:
        idx = int(value, 10)
    except (ValueError, TypeError):
        return None
    if idx < 0:
        return None
    return idx


def classify(update: dict[str, Any], allowed_ids: list[str]) -> dict[str, Any]:
    """Mirror n8n Whitelist JS exactly.

    Parameters
    ----------
    update: raw Telegram update (message or callback_query)
    allowed_ids: parsed list of Telegram user IDs (strings)

    Returns
    -------
    Same shape as Whitelist node output.
    """
    callback_query = update.get("callback_query") or {}
    callback_data = callback_query.get("data") or ""
    feedback_parts = callback_data.split(":") if callback_data.startswith("feedback:") else []
    is_feedback = len(feedback_parts) >= 2
    followup_parts = callback_data.split(":") if callback_data.startswith("followup:") else []
    is_followup = len(followup_parts) == 3
    # Sprint 6 #6 N2 Quick-actions:
    clarify_parts = callback_data.split(":") if callback_data.startswith("clarify:") else []
    is_clarify = len(clarify_parts) == 2
    expand_parts = callback_data.split(":") if callback_data.startswith("expand:") else []
    is_expand = len(expand_parts) == 3

    message = update.get("message") or callback_query.get("message") or {}
    from_obj = (update.get("message") or {}).get("from") or callback_query.get("from") or {}
    message_id = (callback_query.get("message") or {}).get("message_id") or None
    user_message_id = (
        (update.get("message") or {}).get("message_id")
        or (callback_query.get("message") or {}).get("message_id")
        or None
    )
    user_id = str(from_obj.get("id") or "")
    raw_text = message.get("text") or callback_data or ""
    normalized = _normalize(raw_text)
    chat_id = (message.get("chat") or {}).get("id")

    if is_feedback:
        event_type = "feedback"
    elif is_followup:
        event_type = "followup_request"
    elif is_clarify:
        event_type = "clarify_request"
    elif is_expand:
        event_type = "expand_request"
    else:
        event_type = "question"
    text = raw_text
    rating: str | None = None
    category: str | None = None
    request_log_id: str | None = None
    followup_idx: int | None = None

    if is_feedback:
        verb = feedback_parts[1] if len(feedback_parts) > 1 else ""
        request_log_id = feedback_parts[2] if len(feedback_parts) > 2 else None
        if verb == "good":
            rating = "good"
        elif verb == "bad":
            event_type = "feedback_bad_clarify"
            rating = None
        elif verb.startswith("bad_"):
            reason_key = verb[4:]
            if reason_key in REASON_KEYS:
                rating = "bad"
                category = reason_key
            else:
                event_type = "direct_reply"
                text = tg_copy.UNKNOWN_FEEDBACK_REASON_TEXT
        else:
            event_type = "direct_reply"
            text = tg_copy.UNKNOWN_FEEDBACK_TEXT

    if is_followup:
        followup_idx = _safe_int(followup_parts[1])
        request_log_id = followup_parts[2] or None
        if followup_idx is None or not request_log_id:
            event_type = "direct_reply"
            text = tg_copy.UNRECOGNIZED_FOLLOWUP_TEXT

    if is_clarify:
        request_log_id = clarify_parts[1] or None
        if not request_log_id:
            event_type = "direct_reply"
            text = tg_copy.UNRECOGNIZED_FOLLOWUP_TEXT

    if is_expand:
        followup_idx = _safe_int(expand_parts[1])
        request_log_id = expand_parts[2] or None
        if followup_idx is None or not request_log_id:
            event_type = "direct_reply"
            text = tg_copy.UNRECOGNIZED_FOLLOWUP_TEXT

    if not is_feedback and not is_followup and not is_clarify and not is_expand:
        if not normalized:
            event_type = "direct_reply"
            text = tg_copy.EMPTY_INPUT_TEXT
        elif normalized in GREETING_TRIGGERS:
            event_type = "direct_reply"
            text = tg_copy.GREETING_TEXT
        elif normalized in THANKS_TRIGGERS:
            event_type = "direct_reply"
            text = tg_copy.THANKS_TEXT
        elif normalized in {"/help", "help"}:
            event_type = "direct_reply"
            text = tg_copy.HELP_TEXT
        elif normalized in {"/clear", "clear"}:
            event_type = "direct_reply"
            text = tg_copy.CLEAR_TEXT
        elif normalized in {"/history", "history"}:
            event_type = "history_request"
            text = "/history"
        elif normalized in {"/docs", "docs"}:
            event_type = "docs_request"
            text = "/docs"

    if not allowed_ids:
        return {
            "authorized": False,
            "chat_id": chat_id,
            "user_id": user_id,
            "text": (
                f"Whitelist не настроен. Ваш Telegram ID: {user_id}. "
                "Добавьте его в ALLOWED_TELEGRAM_USER_IDS в локальном .env и перезапустите n8n."
            ),
        }
    if user_id not in allowed_ids:
        return {
            "authorized": False,
            "chat_id": chat_id,
            "user_id": user_id,
            "text": f"Доступ запрещен. Ваш Telegram ID: {user_id}.",
        }
    return {
        "authorized": True,
        "user_message_id": user_message_id,
        "event_type": event_type,
        "chat_id": chat_id,
        "message_id": message_id,
        "user_id": user_id,
        "text": text,
        "rating": rating,
        "category": category,
        "request_log_id": request_log_id,
        "followup_idx": followup_idx,
    }


def parse_allowed_ids(raw: str) -> list[str]:
    """ALLOWED_TELEGRAM_USER_IDS=`42,100` → ['42', '100']."""
    return [v.strip() for v in (raw or "").split(",") if v.strip()]
