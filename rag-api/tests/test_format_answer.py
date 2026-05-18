"""Python-native unit tests для `app.format_answer`.

Sprint 8 #1: порт n8n `Format Answer` JS → Python. Эти тесты дублируют
покрытие JS-pin-тестов из `test_n8n_workflow.py::test_format_answer_*`
(parity), плюс точечно покрывают новые сценарии (keyboard, reply_to,
рефьюзал-флаг, dedup, score). После миграции workflow на HTTP-эндпоинт
JS-pin-тесты можно убирать; эти остаются как канонические.
"""
from fastapi.testclient import TestClient

from app.format_answer import (
    TG_MAX_PART,
    balance_tags,
    confidence_chip,
    format_answer,
    looks_refusal,
    md_to_html,
    plural_ru_docs,
    split_into_parts,
)
from app.main import app


CHAT_ID = 42


def _format(payload: dict) -> list[dict]:
    return format_answer(
        answer=payload.get("answer", ""),
        confidence=payload.get("confidence"),
        refused=payload.get("refused", False),
        sources=payload.get("sources"),
        request_log_id=payload.get("request_log_id", "rl"),
        chat_id=payload.get("chat_id", CHAT_ID),
        user_message_id=payload.get("user_message_id"),
    )


# -------- pure helpers --------


def test_md_to_html_converts_code_bold_lists():
    out = md_to_html(
        "**Ответ:** это **controlled zone**.\n- AWB\n- ULD\nПример `controlled_zone_access`."
    )
    assert "<b>Ответ:</b>" in out
    assert "<b>controlled zone</b>" in out
    assert "**" not in out
    assert "<code>controlled_zone_access</code>" in out
    assert "• AWB" in out
    assert "• ULD" in out


def test_md_to_html_does_not_touch_italics_or_links():
    # `*X*` намеренно не трогаем — арифметика 5*8 не должна превратиться в italics
    assert md_to_html("5*8 = 40") == "5*8 = 40"


def test_balance_tags_closes_unclosed():
    assert balance_tags("<b>hello") == "<b>hello</b>"
    assert balance_tags("<code>x") == "<code>x</code>"


def test_balance_tags_opens_unopened():
    assert balance_tags("hello</b>") == "<b>hello</b>"


def test_balance_tags_handles_multiple_tags():
    """Порядок дозакрытия следует _BALANCE_TAGS (b → code → i) — 1:1 с JS-нодой,
    не семантически валидный HTML, но Telegram парсер tolerant к простому
    overlap, главное чтобы opens == closes для каждого тега."""
    out = balance_tags("<b><code>x")
    assert out.count("<b>") == out.count("</b>") == 1
    assert out.count("<code>") == out.count("</code>") == 1


def test_confidence_chip_thresholds():
    assert "Высокая" in confidence_chip(0.9)
    assert "Высокая" in confidence_chip(0.7)
    assert "Средняя" in confidence_chip(0.5)
    assert "Низкая" in confidence_chip(0.1)
    assert confidence_chip(0.0) == ""
    assert confidence_chip(None) == ""


def test_looks_refusal_matches_known_phrases():
    assert looks_refusal("Данных недостаточно.")
    # parity с JS: pattern `нашел?` — необязательная `л`, без ё-варианта.
    # Реальные Mistral-рефьюзалы выдают «нашел/наше», не «нашёл».
    assert looks_refusal("Не нашел в предоставленных источниках.")
    assert looks_refusal("В корпусе нет такой статьи.")
    assert not looks_refusal("Согласно ст. 70 ТК РФ испытательный срок не более 3 месяцев.")


def test_plural_ru_docs():
    assert plural_ru_docs(1) == "релевантный документ"
    assert plural_ru_docs(2) == "релевантных документа"
    assert plural_ru_docs(3) == "релевантных документа"
    assert plural_ru_docs(4) == "релевантных документа"
    assert plural_ru_docs(5) == "релевантных документов"
    assert plural_ru_docs(11) == "релевантных документов"
    assert plural_ru_docs(21) == "релевантный документ"
    assert plural_ru_docs(22) == "релевантных документа"


def test_split_into_parts_short_text_no_split():
    assert split_into_parts("hello") == ["hello"]


def test_split_into_parts_paragraphs():
    para = "X" * 1500
    full = "\n\n".join([para, para, para])  # ~4500 chars
    parts = split_into_parts(full, 2000)
    assert len(parts) >= 2
    for p in parts:
        assert len(p) <= 2000


def test_split_into_parts_handles_giant_sentence():
    huge = "ABCDEFGHIJ" * 1000  # 10000 chars, без \n\n, без знаков препинания
    parts = split_into_parts(huge, 4000)
    assert len(parts) == 3  # 4000+4000+2000
    assert all(len(p) <= 4000 for p in parts)


# -------- format_answer integration --------


def test_format_answer_drops_confidence_text_in_favor_of_summary():
    items = _format(
        {
            "answer": "Краткий ответ.",
            "confidence": 0.7,
            "request_log_id": "rl1",
            "sources": [{"file": "01_hr.md", "section": "Раздел 1", "score": 0.85}],
        }
    )
    text = items[0]["text"]
    assert "Confidence" not in text
    assert "Найдено 1 релевантный документ" in text
    assert "<code>01_hr.md</code>" in text
    assert "Источники:" in text


def test_format_answer_plural_per_count():
    text3 = _format(
        {
            "answer": "x",
            "request_log_id": "rl",
            "sources": [
                {"file": f"f{i}.md", "section": "s", "score": 0.1} for i in range(3)
            ],
        }
    )[0]["text"]
    assert "Найдено 3 релевантных документа" in text3

    text5 = _format(
        {
            "answer": "x",
            "request_log_id": "rl",
            "sources": [
                {"file": f"f{i}.md", "section": "s", "score": 0.1} for i in range(5)
            ],
        }
    )[0]["text"]
    assert "Найдено 5 релевантных документов" in text5


def test_format_answer_html_escapes_user_content():
    text = _format(
        {
            "answer": "Видел <script>alert(1)</script>",
            "request_log_id": "rl",
            "sources": [],
        }
    )[0]["text"]
    assert "<script>" not in text
    assert "&lt;script&gt;" in text


def test_format_answer_converts_markdown_to_html():
    text = _format(
        {
            "answer": "**Ответ:** это **controlled zone**.\n- AWB\n- ULD\nПример `controlled_zone_access`.",
            "request_log_id": "rl",
            "sources": [],
        }
    )[0]["text"]
    assert "<b>Ответ:</b>" in text
    assert "<b>controlled zone</b>" in text
    assert "**" not in text
    assert "<code>controlled_zone_access</code>" in text
    assert "• AWB" in text


def test_format_answer_splits_long_response_with_balanced_tags():
    long_answer = "**Ответ:** " + (
        "Параграф с инфой про controlled zone и aviation security.\n\n" * 100
    )
    items = _format(
        {
            "answer": long_answer,
            "request_log_id": "rl",
            "sources": [
                {"file": f"long_filename_{i:02d}.md", "section": f"Раздел {i}", "score": 0.5}
                for i in range(5)
            ],
        }
    )
    assert len(items) > 1
    for item in items:
        # каждая часть <= 4000 chars + опц. "\n\n<i>часть N/M</i>" суффикс
        assert len(item["text"]) <= TG_MAX_PART + 40
    assert items[-1]["is_last"] is True
    for it in items[:-1]:
        assert it["is_last"] is False
    assert "Найдено" in items[-1]["text"]
    assert "Источники:" in items[-1]["text"]


def test_format_answer_single_part_short_no_part_marker():
    items = _format(
        {
            "answer": "Нормальный ответ на пару предложений.",
            "request_log_id": "rl",
            "sources": [{"file": "a.md", "section": "X", "score": 0.5}],
        }
    )
    assert len(items) == 1
    assert items[0]["is_last"] is True
    assert items[0]["part_total"] == 1
    assert "часть" not in items[0]["text"]


def test_format_answer_multipart_marker_visible():
    long_answer = "Параграф.\n\n" * 400
    items = _format({"answer": long_answer, "request_log_id": "rl", "sources": []})
    assert len(items) >= 2
    for i, it in enumerate(items):
        assert f"часть {i + 1}/{len(items)}" in it["text"]


def test_format_answer_balances_split_bold():
    bolded = "**" + ("очень длинный жирный текст про controlled zone access procedure. " * 80) + "**"
    items = _format({"answer": bolded, "request_log_id": "rl", "sources": []})
    if len(items) > 1:
        for it in items:
            opens = it["text"].count("<b>")
            closes = it["text"].count("</b>")
            assert opens == closes


def test_format_answer_keyboard_only_on_last_part():
    long_answer = "Параграф.\n\n" * 400
    items = _format(
        {
            "answer": long_answer,
            "request_log_id": "rl-abc",
            "sources": [{"file": "f.md", "section": "S", "score": 0.5}],
        }
    )
    assert len(items) >= 2
    for it in items[:-1]:
        assert it["inline_keyboard"] is None
    assert items[-1]["inline_keyboard"] is not None
    assert items[-1]["inline_keyboard"]["inline_keyboard"][-1] == [
        {"text": "👍 Полезно", "callback_data": "feedback:good:rl-abc"},
        {"text": "👎 Неточно", "callback_data": "feedback:bad:rl-abc"},
    ]


def test_format_answer_reply_to_only_on_first_part():
    long_answer = "Параграф.\n\n" * 400
    items = _format(
        {
            "answer": long_answer,
            "request_log_id": "rl",
            "sources": [],
            "user_message_id": 777,
        }
    )
    assert len(items) >= 2
    assert items[0]["reply_to_message_id"] == 777
    for it in items[1:]:
        assert it["reply_to_message_id"] is None


def test_format_answer_dedup_sources_by_file():
    items = _format(
        {
            "answer": "x",
            "request_log_id": "rl",
            "sources": [
                {"file": "a.md", "section": "Раздел 1", "score": 0.8},
                {"file": "a.md", "section": "Раздел 1 копия", "score": 0.7},
                {"file": "b.md", "section": "Другой", "score": 0.6},
            ],
        }
    )
    text = items[0]["text"]
    assert "Найдено 2 релевантных документа" in text
    assert text.count("<code>a.md</code>") == 1
    assert "<code>b.md</code>" in text


def test_format_answer_keyboard_followup_uses_original_idx_after_dedup():
    """После dedup followup callback_data должен ссылаться на ORIGINAL index
    из ответа /ask, не на post-dedup. Это критично для /followup endpoint."""
    items = _format(
        {
            "answer": "x",
            "request_log_id": "rl-x",
            "sources": [
                {"file": "a.md", "section": "S0", "score": 0.9},
                {"file": "a.md", "section": "S0-copy", "score": 0.8},  # dedup
                {"file": "b.md", "section": "S2", "score": 0.7},
                {"file": "c.md", "section": "S3", "score": 0.6},
            ],
        }
    )
    rows = items[-1]["inline_keyboard"]["inline_keyboard"]
    followup_row = rows[0]
    assert len(followup_row) == 2
    callbacks = [btn["callback_data"] for btn in followup_row]
    # original_idx=0 (a.md) и original_idx=2 (b.md). idx=1 (дубль a.md) пропущен.
    assert callbacks == ["followup:0:rl-x", "followup:2:rl-x"]


def test_format_answer_refused_drops_chip_and_adds_next_steps():
    items = _format(
        {
            "answer": "Данных недостаточно для ответа.",
            "confidence": 0.0,
            "refused": True,
            "request_log_id": "rl",
            "sources": [{"file": "near.md", "section": "S", "score": 0.4}],
        }
    )
    text = items[0]["text"]
    assert "уверенность" not in text.lower()
    assert "Что делать дальше" in text
    assert "Ближайшие документы (вне ответа):" in text


def test_format_answer_no_keyboard_without_request_log_id():
    items = _format(
        {
            "answer": "x",
            "request_log_id": "",
            "sources": [{"file": "a.md", "section": "S", "score": 0.5}],
        }
    )
    assert items[-1]["inline_keyboard"] is None


def test_format_answer_quick_row_omits_expand_without_sources():
    items = _format({"answer": "x", "request_log_id": "rl", "sources": []})
    rows = items[-1]["inline_keyboard"]["inline_keyboard"]
    # без источников: followup row пропущен, quick row = только "Уточнить"
    quick = rows[0]
    assert [btn["text"] for btn in quick] == ["🔁 Уточнить"]


# -------- HTTP endpoint --------


def test_format_answer_endpoint_returns_parts():
    client = TestClient(app)
    response = client.post(
        "/tg/format-answer",
        json={
            "answer": "**Ответ:** controlled zone.",
            "confidence": 0.85,
            "refused": False,
            "sources": [{"file": "01_hr.md", "section": "Раздел 1", "score": 0.85}],
            "request_log_id": "rl-1",
            "chat_id": 42,
            "user_message_id": 123,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert "parts" in body
    parts = body["parts"]
    assert len(parts) == 1
    part = parts[0]
    assert part["chat_id"] == 42
    assert part["is_last"] is True
    assert part["part_total"] == 1
    assert part["reply_to_message_id"] == 123
    assert "<b>Ответ:</b> controlled zone." in part["text"]
    assert "<b>Высокая уверенность</b>" in part["text"]
    assert part["inline_keyboard"] is not None


def test_format_answer_endpoint_handles_missing_user_message_id():
    client = TestClient(app)
    response = client.post(
        "/tg/format-answer",
        json={
            "answer": "x",
            "sources": [],
            "request_log_id": "rl",
            "chat_id": 1,
        },
    )
    assert response.status_code == 200
    part = response.json()["parts"][0]
    assert part["reply_to_message_id"] is None
