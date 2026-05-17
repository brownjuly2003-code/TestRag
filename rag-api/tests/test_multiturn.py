"""Sprint 6 #7: unit-тесты augment_retrieval_query + filter_relevant_prev_qas.

A/B live (multi-turn eval Hit@1) — отдельный harness scripts/eval_multiturn.py
требует Docker (postgres + Mistral embeddings).
"""
from __future__ import annotations

import pytest

from app.multiturn import augment_retrieval_query, filter_relevant_prev_qas


# ---------- augment_retrieval_query ----------


def test_augment_empty_prev_returns_current_question():
    assert augment_retrieval_query("Что такое AWB?", []) == "Что такое AWB?"


def test_augment_zero_max_prev_returns_current_question():
    prev = [{"question": "Что такое MAWB?"}]
    assert augment_retrieval_query("А HAWB?", prev, max_prev=0) == "А HAWB?"


def test_augment_includes_prev_questions_in_order():
    prev = [
        {"question": "Что такое MAWB?"},  # most recent
        {"question": "А Cargo manifest?"},  # older
    ]
    out = augment_retrieval_query("А HAWB?", prev, max_prev=2)
    # Текущий вопрос — последним; prev в order desc по created_at (как recent_requests)
    assert out == "Что такое MAWB? | А Cargo manifest? | А HAWB?"


def test_augment_respects_max_prev_limit():
    prev = [{"question": f"q{i}"} for i in range(5)]
    out = augment_retrieval_query("current", prev, max_prev=2)
    assert out == "q0 | q1 | current"


def test_augment_skips_empty_prev_questions():
    prev = [{"question": ""}, {"question": "  "}, {"question": "Real Q"}]
    out = augment_retrieval_query("now", prev, max_prev=3)
    assert out == "Real Q | now"


def test_augment_include_answers_optional():
    prev = [{"question": "Что AWB?", "answer": "AWB = Air Waybill."}]
    out = augment_retrieval_query("А cargo manifest?", prev, max_prev=1, include_answers=True)
    assert "AWB = Air Waybill." in out
    assert "А cargo manifest?" in out


def test_augment_excludes_answers_by_default():
    prev = [{"question": "Что AWB?", "answer": "AWB = Air Waybill."}]
    out = augment_retrieval_query("А cargo manifest?", prev, max_prev=1)
    assert "AWB = Air Waybill." not in out
    assert out == "Что AWB? | А cargo manifest?"


def test_augment_empty_current_question_returns_unchanged():
    prev = [{"question": "q"}]
    assert augment_retrieval_query("", prev) == ""


# ---------- filter_relevant_prev_qas ----------


def test_filter_skips_refused_turns_by_default():
    qas = [
        {"question": "Q1", "refused": False, "confidence": 0.8},
        {"question": "Q2", "refused": True, "confidence": 0.0},
        {"question": "Q3", "refused": False, "confidence": 0.5},
    ]
    out = filter_relevant_prev_qas(qas)
    assert [q["question"] for q in out] == ["Q1", "Q3"]


def test_filter_respects_min_confidence():
    qas = [
        {"question": "Q1", "refused": False, "confidence": 0.8},
        {"question": "Q2", "refused": False, "confidence": 0.2},
        {"question": "Q3", "refused": False, "confidence": 0.5},
    ]
    out = filter_relevant_prev_qas(qas, min_confidence=0.4)
    assert [q["question"] for q in out] == ["Q1", "Q3"]


def test_filter_keeps_qas_with_none_confidence():
    """confidence=None — старые логи без recalibration. Не отбрасываем."""
    qas = [
        {"question": "Q1", "refused": False, "confidence": None},
        {"question": "Q2", "refused": False, "confidence": 0.9},
    ]
    out = filter_relevant_prev_qas(qas, min_confidence=0.5)
    assert [q["question"] for q in out] == ["Q1", "Q2"]


def test_filter_can_keep_refused_when_disabled():
    qas = [{"question": "Q1", "refused": True}]
    out = filter_relevant_prev_qas(qas, skip_refused=False)
    assert len(out) == 1


# ---------- /ask integration via FakeStore ----------


def test_ask_with_prev_qa_count_augments_retrieval_query(monkeypatch):
    """/ask?prev_qa_count=2 + telegram_user_id → store.recent_requests читается,
    retriever.search получает augmented строку."""
    from fastapi.testclient import TestClient
    from app.main import app
    from app import main as main_mod  # noqa: F401

    # Используем FakeStore из test_api для consistency
    from test_api import FakeStore, runtime_with_store

    store = FakeStore()
    # recent_requests() в FakeStore возвращает фиксированный hardcoded item;
    # переопределим, чтобы вернуть multi-turn последовательность.
    def fake_recent(telegram_user_id, limit=5):
        return [
            {"id": "rl-2", "question": "Что такое controlled zone?", "answer": "", "confidence": 0.9, "refused": False, "created_at": "2026-05-17T01:00:00"},
            {"id": "rl-1", "question": "Что такое AWB?", "answer": "", "confidence": 0.8, "refused": False, "created_at": "2026-05-17T00:55:00"},
        ][:limit]
    store.recent_requests = fake_recent  # type: ignore[assignment]

    captured: dict[str, str] = {}

    def spy_search(query, **kwargs):
        captured["query"] = query
        return []

    runtime = runtime_with_store(store)

    class SpyRetriever:
        def search(self, query, **kwargs):
            captured["query"] = query
            return []

    runtime = runtime.__class__(
        chunks=runtime.chunks,
        retriever=SpyRetriever(),
        policy=runtime.policy,
        llm=runtime.llm,
        embeddings=runtime.embeddings,
        store=runtime.store,
    )
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime)

    with TestClient(app) as client:
        resp = client.post("/ask", json={
            "question": "А кто туда имеет доступ?",
            "telegram_user_id": "42",
            "prev_qa_count": 2,
        })

    assert resp.status_code == 200
    # augmented retrieval query содержит prev questions + current
    assert "controlled zone" in captured["query"]
    assert "AWB" in captured["query"]
    assert "А кто туда имеет доступ?" in captured["query"]


def test_ask_without_prev_qa_count_uses_current_question_only(monkeypatch):
    """default prev_qa_count=0 → augmentation отключена."""
    from fastapi.testclient import TestClient
    from app.main import app
    from test_api import FakeStore, runtime_with_store

    store = FakeStore()
    captured: dict[str, str] = {}
    runtime = runtime_with_store(store)

    class SpyRetriever:
        def search(self, query, **kwargs):
            captured["query"] = query
            return []

    runtime = runtime.__class__(
        chunks=runtime.chunks,
        retriever=SpyRetriever(),
        policy=runtime.policy,
        llm=runtime.llm,
        embeddings=runtime.embeddings,
        store=runtime.store,
    )
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime)

    with TestClient(app) as client:
        resp = client.post("/ask", json={
            "question": "Что такое AWB?",
            "telegram_user_id": "42",
        })

    assert resp.status_code == 200
    assert captured["query"] == "Что такое AWB?"  # не augmented


def test_ask_with_prev_qa_count_but_no_user_id_skips_augmentation(monkeypatch):
    """Без telegram_user_id history недоступен → ignore prev_qa_count."""
    from fastapi.testclient import TestClient
    from app.main import app
    from test_api import FakeStore, runtime_with_store

    store = FakeStore()
    captured: dict[str, str] = {}
    runtime = runtime_with_store(store)

    class SpyRetriever:
        def search(self, query, **kwargs):
            captured["query"] = query
            return []

    runtime = runtime.__class__(
        chunks=runtime.chunks,
        retriever=SpyRetriever(),
        policy=runtime.policy,
        llm=runtime.llm,
        embeddings=runtime.embeddings,
        store=runtime.store,
    )
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime)

    with TestClient(app) as client:
        resp = client.post("/ask", json={
            "question": "А кто туда имеет доступ?",
            "prev_qa_count": 2,
            # no telegram_user_id
        })

    assert resp.status_code == 200
    assert captured["query"] == "А кто туда имеет доступ?"
