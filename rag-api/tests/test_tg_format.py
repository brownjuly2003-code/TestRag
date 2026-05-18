"""Sprint 8 #2 (codex-audit#5.1) Python-native parity tests для tg_format."""
from fastapi.testclient import TestClient

from app.main import app
from app.tg_format import format_docs, format_history


# -------- format_history --------


def test_format_history_empty_returns_prompt():
    text = format_history([])
    assert "пуста" in text.lower()
    assert "/history" in text


def test_format_history_singular():
    items = [
        {"question": "Что такое controlled zone?", "created_at": "2026-05-17T10:30:00", "refused": False}
    ]
    text = format_history(items)
    assert text.startswith("<b>Последний 1 запрос:</b>")
    assert "<code>Что такое controlled zone?</code>" in text
    assert "<b>2026-05-17 10:30</b>" in text


def test_format_history_paucal_2_to_4():
    items = [{"question": f"q{i}", "created_at": "2026-05-17T10:30:00"} for i in range(3)]
    assert format_history(items).startswith("<b>Последние 3 запроса:</b>")


def test_format_history_plural_5_plus():
    items = [{"question": f"q{i}", "created_at": "2026-05-17T10:30:00"} for i in range(5)]
    assert format_history(items).startswith("<b>Последние 5 запросов:</b>")


def test_format_history_refused_tag():
    items = [{"question": "x", "created_at": "2026-05-17T10:30:00", "refused": True}]
    assert " [отказ]" in format_history(items)


def test_format_history_truncates_long_question_to_120():
    long_q = "А" * 200
    items = [{"question": long_q, "created_at": "2026-05-17T10:30:00"}]
    text = format_history(items)
    # 120 chars in <code>...</code>
    assert "<code>" + ("А" * 120) + "</code>" in text
    assert ("А" * 121) not in text


def test_format_history_html_escapes_question():
    items = [{"question": "<script>alert(1)</script>", "created_at": "2026-05-17T10:30:00"}]
    text = format_history(items)
    assert "<script>" not in text
    assert "&lt;script&gt;" in text


# -------- format_docs --------


def test_format_docs_empty_categories():
    text = format_docs([], 0)
    assert "пуст" in text.lower() or "не загружен" in text.lower()


def test_format_docs_renders_categories_with_samples():
    categories = [
        {
            "category": "01_hr_pol",
            "label": "HR — политики",
            "doc_count": 5,
            "sample_files": ["01_hr_pol_safety.md", "01_hr_pol_dress.md", "01_hr_pol_third.md"],
        }
    ]
    text = format_docs(categories, 48)
    assert "<b>Корпус знаний: 48 документов</b>" in text
    assert "<b>HR — политики</b> (5)" in text
    # only 2 sample files shown
    assert "<code>01_hr_pol_safety.md</code>" in text
    assert "<code>01_hr_pol_dress.md</code>" in text
    assert "01_hr_pol_third.md" not in text


def test_format_docs_category_without_samples_omits_tail():
    categories = [{"label": "Без примеров", "doc_count": 2, "sample_files": []}]
    text = format_docs(categories, 2)
    assert "• <b>Без примеров</b> (2)\n" in text
    assert "например" not in text


def test_format_docs_html_escapes_label_and_files():
    categories = [
        {"label": "Cat <script>", "doc_count": 1, "sample_files": ["bad<x>.md"]},
    ]
    text = format_docs(categories, 1)
    assert "<script>" not in text
    assert "&lt;script&gt;" in text
    assert "&lt;x&gt;" in text


# -------- endpoints --------


def test_endpoint_format_history():
    client = TestClient(app)
    response = client.post(
        "/tg/format-history",
        json={"items": [{"question": "Q1", "created_at": "2026-05-17T10:30:00"}]},
    )
    assert response.status_code == 200
    assert "Q1" in response.json()["text"]


def test_endpoint_format_docs():
    client = TestClient(app)
    response = client.post(
        "/tg/format-docs",
        json={
            "categories": [
                {"label": "Lab", "doc_count": 3, "sample_files": ["f.md"]}
            ],
            "total_docs": 3,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert "<b>Корпус знаний: 3 документов</b>" in body["text"]
    assert "<b>Lab</b> (3)" in body["text"]


def test_endpoint_format_history_empty():
    client = TestClient(app)
    response = client.post("/tg/format-history", json={"items": []})
    assert response.status_code == 200
    assert "/history" in response.json()["text"]


def test_endpoint_feedback_copy_blocks():
    """codex-audit#5.1 close: Format Feedback (JS, 6 строк) → static в tg_copy."""
    client = TestClient(app)
    default_text = client.get("/tg/copy/feedback_default").json()["text"]
    human_text = client.get("/tg/copy/feedback_human").json()["text"]
    assert default_text == "Оценка принята."
    assert "HR/Legal" in human_text
