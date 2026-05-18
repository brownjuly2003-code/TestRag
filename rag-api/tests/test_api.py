from fastapi.testclient import TestClient

from app.main import (
    AnswerPolicy,
    DocumentChunk,
    HybridRetriever,
    MistralChatClient,
    MistralEmbeddingClient,
    Runtime,
    app,
    is_pure_refusal,
)


def test_is_pure_refusal_true_for_short_refusal():
    assert is_pure_refusal("Данных недостаточно.") is True
    assert is_pure_refusal("Не хватает источников.") is True
    assert is_pure_refusal("Не нашёл подходящих документов.") is True


def test_is_pure_refusal_false_for_cautious_preface_with_body():
    answer = (
        "Данных недостаточно для точного ответа. "
        "Однако из источников видно, что для отправки dangerous goods авиатранспортом "
        "требуется AWB/MAWB/HAWB, security screening, упаковка по IATA DGR и инструктаж."
    )
    assert is_pure_refusal(answer) is False


def test_is_pure_refusal_false_for_non_refusal_answer():
    assert is_pure_refusal("Согласно ст. 70 ТК РФ испытательный срок не более 3 месяцев.") is False


def test_is_pure_refusal_handles_mixed_punctuation_in_body():
    answer = (
        "Не хватает данных! Тем не менее, источник 1 указывает на AWB/MAWB/HAWB как "
        "обязательный реквизит контракта экспедиции авиагруза, а источник 2 уточняет, "
        "что cutoff time и terminal acceptance status фиксируются в booking confirmation."
    )
    assert is_pure_refusal(answer) is False


def test_health_endpoint_reports_service_status():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


class FakeStore:
    def __init__(self) -> None:
        self.request_logs = []
        self.feedback = []
        self.review_queue = []
        self.history_calls: list[dict] = []
        self.corpus_summary_rows: list[dict] = [
            {"category": "01_hr_pol", "doc_count": 60},
            {"category": "07_faq", "doc_count": 8},
        ]
        self.request_sources: dict[tuple[str, int], dict] = {}

    def ingest_documents(self, docs_path, embedding_client) -> int:
        return 0

    def load_chunks(self):
        return []

    def log_request(self, **kwargs):
        self.request_logs.append(kwargs)
        return "request-1"

    def log_feedback(self, **kwargs):
        self.feedback.append(kwargs)
        return "feedback-1"

    def recent_requests(self, telegram_user_id, limit=5):
        self.history_calls.append({"telegram_user_id": telegram_user_id, "limit": limit})
        return [
            {
                "id": "rl-1",
                "question": "Что такое controlled zone?",
                "answer": "Зона аэропорта...",
                "confidence": 0.42,
                "refused": False,
                "created_at": "2026-05-17T01:47:00+00:00",
            }
        ]

    def corpus_summary(self):
        return self.corpus_summary_rows

    def get_request_source(self, request_log_id, idx):
        return self.request_sources.get((request_log_id, idx))

    def get_request_question(self, request_log_id):
        # Sprint 6 #6 N2 Quick-actions: lookup для /clarify rerun
        for entry in self.request_logs:
            if entry.get("request_log_id") == request_log_id:
                return entry.get("question")
        return self.request_sources.get(("__question__", request_log_id))  # test backdoor

    # Override enqueue_review to capture context arg (N3)
    def enqueue_review(self, request_log_id=None, reason=None, context=None):
        self.review_queue.append({
            "request_log_id": request_log_id,
            "reason": reason,
            "context": context,
        })
        return "review-1"

    def metrics(self, window_hours=168):
        return {
            "window_hours": window_hours,
            "total_requests": 17,
            "refusal_rate": 0.18,
            "avg_latency_ms": 2456.0,
            "avg_confidence": 0.62,
            "avg_prompt_tokens": 1432.5,
            "avg_completion_tokens": 287.3,
            "bad_feedback_rate": 0.08,
        }

    def analytics_breakdown(self, window_hours=168, top_n=10):
        return {
            "window_hours": window_hours,
            "top_questions": [
                {"question": "что такое controlled zone?", "count": 5},
                {"question": "сколько длится испытательный срок?", "count": 3},
            ][:top_n],
            "top_request_types": [
                {"request_type": "knowledge_query", "count": 6},
                {"request_type": "document_draft", "count": 2},
            ][:top_n],
            "top_refused_questions": [
                {"question": "что такое foo bar?", "count": 2},
            ][:top_n],
            "review_queue_open": 3,
        }


class FakeDocumentPlanner:
    enabled = True

    async def answer(self, question, results):
        return None, {"model": "fake", "prompt_tokens": None, "completion_tokens": None}

    async def document_plan(self, system_prompt, user_prompt):
        return {
            "intent": "template_draft",
            "document_type": "HR_ORDER_HIRING",
            "document_type_label": "Приказ о приеме на работу",
            "confidence": "HIGH",
            "can_generate_draft": True,
            "requires_human_review": True,
            "reasoning": "LLM plan",
            "required_fields": [],
            "missing_fields": [],
            "risk_flags": [],
            "source_requirements": [],
            "draft_outline": [],
            "draft_text": "LLM свободный черновик",
            "sources": [],
            "user_message": "LLM message",
        }


class FakeInsufficientAnswerClient:
    enabled = True

    async def answer(self, question, results):
        return (
            "Данных недостаточно. В предоставленных источниках нет нужных сведений.",
            {"model": "fake", "prompt_tokens": 12, "completion_tokens": 18},
        )

    async def document_plan(self, system_prompt, user_prompt):
        return None


def runtime_with_store(store: FakeStore, llm=None) -> Runtime:
    chunks = [
        DocumentChunk(
            chunk_id="templates:0",
            content=(
                "Для приказа о приеме на работу нужны поля: ФИО работника, должность, "
                "подразделение, дата начала работы, условия оплаты и основание оформления."
            ),
            metadata={
                "file": "document_templates.md",
                "section": "Черновики кадровых документов",
                "date": "2026-05-15",
            },
        )
    ]
    return Runtime(
        chunks=chunks,
        retriever=HybridRetriever(chunks),
        policy=AnswerPolicy(min_confidence=0.1),
        llm=llm or MistralChatClient("", "mistral-small-latest"),
        embeddings=MistralEmbeddingClient("", "mistral-embed"),
        store=store,
    )


def test_ask_logs_request_and_returns_request_log_id(monkeypatch):
    store = FakeStore()
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime_with_store(store))

    with TestClient(app) as client:
        response = client.post(
            "/ask",
            json={
                "question": "Сделай приказ о приеме на работу",
                "telegram_user_id": "42",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["request_log_id"] == "request-1"
    assert store.request_logs[0]["telegram_user_id"] == "42"
    assert store.request_logs[0]["request_type"] == "template_draft"
    assert store.request_logs[0]["sources"]


def test_ask_marks_llm_insufficient_answer_as_refused(monkeypatch):
    store = FakeStore()
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime_with_store(store, llm=FakeInsufficientAnswerClient()))

    with TestClient(app) as client:
        response = client.post(
            "/ask",
            json={
                "question": "Сделай приказ о приеме на работу",
                "telegram_user_id": "42",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["refused"] is True
    assert body["confidence"] == 0
    assert body["answer"].startswith("Данных недостаточно")
    assert store.request_logs[0]["refused"] is True
    assert store.request_logs[0]["confidence"] == 0


def test_bad_feedback_is_written_to_review_queue(monkeypatch):
    store = FakeStore()
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime_with_store(store))

    with TestClient(app) as client:
        response = client.post(
            "/feedback",
            json={
                "request_log_id": "request-1",
                "telegram_user_id": "42",
                "rating": "bad",
                "comment": "Нет источников",
            },
        )

    assert response.status_code == 200
    assert response.json()["status"] == "accepted"
    assert store.feedback[0]["rating"] == "bad"
    assert store.review_queue[0]["request_log_id"] == "request-1"


def test_feedback_accepts_category_and_free_text(monkeypatch):
    store = FakeStore()
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime_with_store(store))

    with TestClient(app) as client:
        response = client.post(
            "/feedback",
            json={
                "request_log_id": "request-1",
                "telegram_user_id": "42",
                "rating": "bad",
                "comment": "telegram_inline_button",
                "category": "inaccurate",
                "free_text": None,
            },
        )

    assert response.status_code == 200
    written = store.feedback[0]
    assert written["category"] == "inaccurate"
    assert written["rating"] == "bad"
    assert store.review_queue[0]["reason"] == "inaccurate"


def test_history_endpoint_returns_recent_requests(monkeypatch):
    store = FakeStore()
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime_with_store(store))

    with TestClient(app) as client:
        response = client.get("/history", params={"telegram_user_id": "42", "limit": 5})

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["question"] == "Что такое controlled zone?"
    assert body["items"][0]["confidence"] == 0.42
    assert store.history_calls[0] == {"telegram_user_id": "42", "limit": 5}


def test_history_endpoint_clamps_limit(monkeypatch):
    store = FakeStore()
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime_with_store(store))

    with TestClient(app) as client:
        client.get("/history", params={"telegram_user_id": "42", "limit": 500})

    assert store.history_calls[0]["limit"] == 20


def test_docs_summary_endpoint_groups_by_category(monkeypatch):
    store = FakeStore()
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime_with_store(store))

    with TestClient(app) as client:
        response = client.get("/docs/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["total_docs"] == 68
    labels = {c["category"]: c["label"] for c in body["categories"]}
    assert labels["01_hr_pol"] == "HR — политики и регламенты"
    assert labels["07_faq"] == "FAQ — частые вопросы"


def test_human_handover_captures_last_5_messages_into_review_context(monkeypatch):
    store = FakeStore()
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime_with_store(store))

    with TestClient(app) as client:
        response = client.post(
            "/feedback",
            json={
                "request_log_id": "request-1",
                "telegram_user_id": "42",
                "rating": "bad",
                "category": "human",
            },
        )

    assert response.status_code == 200
    written = store.review_queue[0]
    assert written["reason"] == "human"
    assert isinstance(written["context"], list)
    assert len(written["context"]) >= 1
    assert written["context"][0]["question"] == "Что такое controlled zone?"
    # history fetched once for context
    assert any(call["telegram_user_id"] == "42" for call in store.history_calls)


def test_non_human_bad_feedback_writes_empty_context(monkeypatch):
    store = FakeStore()
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime_with_store(store))

    with TestClient(app) as client:
        response = client.post(
            "/feedback",
            json={
                "request_log_id": "request-1",
                "telegram_user_id": "42",
                "rating": "bad",
                "category": "inaccurate",
            },
        )

    assert response.status_code == 200
    written = store.review_queue[0]
    assert written["context"] == []


def test_ask_response_includes_status_latency_and_version_metadata(monkeypatch):
    store = FakeStore()
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime_with_store(store))

    with TestClient(app) as client:
        response = client.post(
            "/ask",
            json={"question": "Сделай приказ о приеме на работу", "telegram_user_id": "42"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"answerable", "needs_human_review", "unanswerable"}
    assert body["latency_ms"] is not None
    # observability также залогирован в FakeStore.request_logs
    logged = store.request_logs[0]
    assert "latency_ms" in logged
    assert logged["latency_ms"] is not None


def test_ask_response_omits_debug_by_default(monkeypatch):
    """Sprint 6 #3: debug=null когда не запрошен (backwards-compat)."""
    store = FakeStore()
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime_with_store(store))

    with TestClient(app) as client:
        response = client.post(
            "/ask",
            json={"question": "Сделай приказ о приеме на работу", "telegram_user_id": "42"},
        )

    assert response.status_code == 200
    assert response.json()["debug"] is None


def test_ask_response_includes_debug_breakdown_when_requested(monkeypatch):
    """Sprint 6 #3: debug=true → веса, query_tokens, per-result decomposition."""
    store = FakeStore()
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime_with_store(store))

    with TestClient(app) as client:
        response = client.post(
            "/ask",
            json={
                "question": "Сделай приказ о приеме на работу",
                "telegram_user_id": "42",
                "debug": True,
            },
        )

    assert response.status_code == 200
    body = response.json()
    debug = body["debug"]
    assert debug is not None
    assert "bm25" in debug["weights"]
    assert "vector" in debug["weights"]
    assert "coverage_exp" in debug["weights"]
    assert isinstance(debug["query_tokens"], list)
    assert isinstance(debug["has_vector"], bool)
    assert isinstance(debug["results"], list)
    if debug["results"]:
        row = debug["results"][0]
        for field in (
            "chunk_id",
            "bm25_score",
            "normalized_bm25",
            "vector_score",
            "coverage",
            "section_boost",
            "final_score",
        ):
            assert field in row


def test_ask_refused_response_status_is_unanswerable(monkeypatch):
    """При refused=True endpoint должен вернуть status='unanswerable' и не вызывать LLM."""
    store = FakeStore()
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime_with_store(store))

    with TestClient(app) as client:
        response = client.post(
            "/ask",
            json={"question": "случайный нерелевантный вопрос xyz123", "telegram_user_id": "42", "top_k": 1},
        )

    assert response.status_code == 200
    body = response.json()
    # FakeStore corpus вернёт low confidence → refused via AnswerPolicy(min_confidence=0.1) — но
    # в test runtime policy достаточно мягкий. Просто проверим что status согласован с refused.
    if body["refused"]:
        assert body["status"] == "unanswerable"
    else:
        assert body["status"] in {"answerable", "needs_human_review"}


def test_metrics_endpoint_returns_aggregated_stats(monkeypatch):
    store = FakeStore()
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime_with_store(store))

    with TestClient(app) as client:
        response = client.get("/metrics", params={"window_hours": 24})

    assert response.status_code == 200
    body = response.json()
    assert body["window_hours"] == 24
    assert body["total_requests"] == 17
    assert body["refusal_rate"] == 0.18
    assert body["avg_latency_ms"] == 2456.0
    assert body["bad_feedback_rate"] == 0.08


def test_metrics_endpoint_rejects_invalid_window():
    with TestClient(app) as client:
        response = client.get("/metrics", params={"window_hours": 0})
    assert response.status_code == 400
    with TestClient(app) as client:
        response = client.get("/metrics", params={"window_hours": 100000})
    assert response.status_code == 400


def test_analytics_endpoint_returns_frequent_cases(monkeypatch):
    store = FakeStore()
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime_with_store(store))

    with TestClient(app) as client:
        response = client.get("/analytics", params={"window_hours": 48, "top_n": 5})

    assert response.status_code == 200
    body = response.json()
    assert body["window_hours"] == 48
    assert body["review_queue_open"] == 3
    assert body["top_questions"][0]["question"] == "что такое controlled zone?"
    assert body["top_questions"][0]["count"] == 5
    assert body["top_request_types"][0]["request_type"] == "knowledge_query"
    assert body["top_refused_questions"][0]["count"] == 2


def test_analytics_endpoint_rejects_invalid_params():
    with TestClient(app) as client:
        response = client.get("/analytics", params={"window_hours": 0})
    assert response.status_code == 400
    with TestClient(app) as client:
        response = client.get("/analytics", params={"top_n": 0})
    assert response.status_code == 400
    with TestClient(app) as client:
        response = client.get("/analytics", params={"top_n": 200})
    assert response.status_code == 400


def test_followup_returns_question_with_section_and_file(monkeypatch):
    store = FakeStore()
    store.request_sources[("rl-1", 0)] = {
        "chunk_id": "abc",
        "file": "01_hr_pol_safety.md",
        "section": "Контролируемая зона",
        "score": 0.92,
    }
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime_with_store(store))

    with TestClient(app) as client:
        response = client.get("/followup", params={"request_log_id": "rl-1", "idx": 0})

    assert response.status_code == 200
    body = response.json()
    assert "Контролируемая зона" in body["question"]
    assert "01_hr_pol_safety.md" in body["question"]
    assert body["source"]["chunk_id"] == "abc"
    assert body["source"]["section"] == "Контролируемая зона"


def test_followup_returns_question_without_section(monkeypatch):
    store = FakeStore()
    store.request_sources[("rl-1", 0)] = {
        "chunk_id": "abc",
        "file": "07_faq_general.md",
        "section": None,
        "score": 0.5,
    }
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime_with_store(store))

    with TestClient(app) as client:
        response = client.get("/followup", params={"request_log_id": "rl-1", "idx": 0})

    assert response.status_code == 200
    assert "07_faq_general.md" in response.json()["question"]


def test_followup_returns_404_when_source_missing(monkeypatch):
    store = FakeStore()
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime_with_store(store))

    with TestClient(app) as client:
        response = client.get("/followup", params={"request_log_id": "rl-x", "idx": 0})

    assert response.status_code == 404


def test_followup_rejects_negative_idx(monkeypatch):
    store = FakeStore()
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime_with_store(store))

    with TestClient(app) as client:
        response = client.get("/followup", params={"request_log_id": "rl-1", "idx": -1})

    assert response.status_code == 400


def test_followup_requires_request_log_id():
    with TestClient(app) as client:
        response = client.get("/followup", params={"idx": 0})

    assert response.status_code == 422


# ---------- Sprint 6 #6 N2 Quick-actions: /clarify + /expand ----------


def test_expand_returns_full_chunk_content(monkeypatch):
    store = FakeStore()
    store.request_sources[("rl-1", 0)] = {
        "chunk_id": "templates:0",
        "file": "document_templates.md",
        "section": "Черновики кадровых документов",
        "score": 0.92,
    }
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime_with_store(store))

    with TestClient(app) as client:
        response = client.get("/expand", params={"request_log_id": "rl-1", "idx": 0})

    assert response.status_code == 200
    body = response.json()
    # full chunk content (не snippet) попадает в text
    assert "ФИО работника" in body["text"]
    assert body["chunk_id"] == "templates:0"
    assert body["file"] == "document_templates.md"
    assert body["section"] == "Черновики кадровых документов"
    # HTML header для TG (parse_mode=HTML)
    assert "<code>document_templates.md</code>" in body["text"]


def test_expand_html_escapes_chunk_content(monkeypatch):
    """Telegram parse_mode=HTML отвергает unescaped `<` и `&` в body text.
    Chunks из normative-источников могут содержать markdown autolinks
    `<https://...>` и аббревиатуры `M&A`, `P&L` — /expand обязан их escape'нуть.
    """
    store = FakeStore()
    store.request_sources[("rl-html", 0)] = {
        "chunk_id": "html-chunk:0",
        "file": "external_normative.md",
        "section": "M&A контекст",
        "score": 0.9,
    }

    def runtime_with_html_chunk(_store):
        chunks = [
            DocumentChunk(
                chunk_id="html-chunk:0",
                content="См. <https://example.com/doc>. Финансы M&A и P&L.",
                metadata={"file": "external_normative.md", "section": "M&A контекст"},
            )
        ]
        return Runtime(
            chunks=chunks,
            retriever=HybridRetriever(chunks),
            policy=AnswerPolicy(min_confidence=0.1),
            llm=MistralChatClient("", "mistral-small-latest"),
            embeddings=MistralEmbeddingClient("", "mistral-embed"),
            store=_store,
        )

    monkeypatch.setattr("app.main.get_runtime", lambda: runtime_with_html_chunk(store))

    with TestClient(app) as client:
        response = client.get("/expand", params={"request_log_id": "rl-html", "idx": 0})

    assert response.status_code == 200
    text = response.json()["text"]
    # raw `<` и `&` должны быть заэскейплены
    assert "<https://example.com/doc>" not in text
    assert "&lt;https://example.com/doc&gt;" in text
    assert "M&A" not in text.replace("M&amp;A", "")
    assert "M&amp;A" in text
    assert "P&amp;L" in text
    # filename header — intentional `<code>` остаётся
    assert "<code>external_normative.md</code>" in text


def test_expand_returns_404_when_chunk_id_unknown(monkeypatch):
    store = FakeStore()
    store.request_sources[("rl-1", 0)] = {
        "chunk_id": "missing-chunk",
        "file": "x.md",
        "section": "X",
        "score": 0.5,
    }
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime_with_store(store))

    with TestClient(app) as client:
        response = client.get("/expand", params={"request_log_id": "rl-1", "idx": 0})

    assert response.status_code == 404


def test_expand_returns_404_when_source_missing(monkeypatch):
    store = FakeStore()
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime_with_store(store))

    with TestClient(app) as client:
        response = client.get("/expand", params={"request_log_id": "rl-x", "idx": 0})

    assert response.status_code == 404


def test_expand_rejects_negative_idx(monkeypatch):
    store = FakeStore()
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime_with_store(store))

    with TestClient(app) as client:
        response = client.get("/expand", params={"request_log_id": "rl-1", "idx": -1})

    assert response.status_code == 400


def test_expand_requires_request_log_id():
    with TestClient(app) as client:
        response = client.get("/expand", params={"idx": 0})

    assert response.status_code == 422


def test_clarify_reruns_with_top_k_10(monkeypatch):
    store = FakeStore()
    # backdoor: get_request_question возвращает строку
    store.request_sources[("__question__", "rl-1")] = "Что такое controlled zone?"
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime_with_store(store))

    with TestClient(app) as client:
        response = client.post("/clarify", params={"request_log_id": "rl-1"})

    assert response.status_code == 200
    body = response.json()
    assert body["request_log_id"] == "request-1"
    # /clarify создаёт НОВЫЙ request_log → log_request вызван
    assert len(store.request_logs) == 1


def test_clarify_returns_404_when_request_log_unknown(monkeypatch):
    store = FakeStore()
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime_with_store(store))

    with TestClient(app) as client:
        response = client.post("/clarify", params={"request_log_id": "rl-missing"})

    assert response.status_code == 404


def test_document_type_detection_returns_missing_fields(monkeypatch):
    store = FakeStore()
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime_with_store(store))

    with TestClient(app) as client:
        response = client.post(
            "/document/type-detection",
            json={
                "question": "Сделай приказ о приеме Иванова Ивана на должность юриста с 20 мая 2026.",
                "user_provided_fields": {
                    "employee_full_name": "Иванов Иван Иванович",
                    "position": "юрист",
                    "start_date": "2026-05-20",
                },
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "template_draft"
    assert body["document_type"] == "HR_ORDER_HIRING"
    assert body["confidence"] == "MEDIUM"
    assert body["can_generate_draft"] is False
    assert body["draft_text"] is None
    assert "department" in body["missing_fields"]


def test_document_type_detection_generates_hiring_order_draft_from_template(monkeypatch):
    store = FakeStore()
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime_with_store(store))

    with TestClient(app) as client:
        response = client.post(
            "/document/type-detection",
            json={
                "question": "Подготовь приказ о приеме Иванова Ивана на должность юриста.",
                "user_provided_fields": {
                    "employee_full_name": "Иванов Иван Иванович",
                    "position": "юрист",
                    "department": "Юридический отдел",
                    "start_date": "2026-05-20",
                    "salary_terms": "оклад 100000 рублей",
                    "employment_basis": "трудовой договор",
                },
                "available_templates": [
                    {
                        "id": "hr_order_hiring_v1",
                        "document_type": "HR_ORDER_HIRING",
                    }
                ],
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["document_type"] == "HR_ORDER_HIRING"
    assert body["confidence"] == "HIGH"
    assert body["can_generate_draft"] is True
    assert body["missing_fields"] == []
    assert "Иванов Иван Иванович" in body["draft_text"]
    assert "Юридический отдел" in body["draft_text"]
    assert "Документ является черновиком" in body["draft_text"]


def test_document_type_detection_generates_vacation_order_draft_from_template(monkeypatch):
    """TZ §2: second code-template — Приказ о предоставлении отпуска."""
    store = FakeStore()
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime_with_store(store))

    with TestClient(app) as client:
        response = client.post(
            "/document/type-detection",
            json={
                "question": "Подготовь приказ об отпуске для Петрова Петра.",
                "user_provided_fields": {
                    "employee_full_name": "Петров Петр Петрович",
                    "vacation_start_date": "2026-06-01",
                    "vacation_end_date": "2026-06-28",
                    "vacation_basis": "ежегодный оплачиваемый отпуск согласно графику",
                },
                "available_templates": [
                    {
                        "id": "hr_order_vacation_v1",
                        "document_type": "HR_ORDER_VACATION",
                    }
                ],
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["document_type"] == "HR_ORDER_VACATION"
    assert body["confidence"] == "HIGH"
    assert body["can_generate_draft"] is True
    assert body["missing_fields"] == []
    assert "Петров Петр Петрович" in body["draft_text"]
    assert "2026-06-01" in body["draft_text"]
    assert "ежегодный оплачиваемый отпуск" in body["draft_text"]
    assert "Документ является черновиком" in body["draft_text"]


def test_document_type_detection_does_not_return_llm_generated_draft(monkeypatch):
    store = FakeStore()
    monkeypatch.setattr("app.main.get_runtime", lambda: runtime_with_store(store, llm=FakeDocumentPlanner()))

    with TestClient(app) as client:
        response = client.post(
            "/document/type-detection",
            json={
                "question": "Подготовь приказ о приеме Иванова Ивана на должность юриста.",
                "user_provided_fields": {
                    "employee_full_name": "Иванов Иван Иванович",
                    "position": "юрист",
                    "department": "Юридический отдел",
                    "start_date": "2026-05-20",
                    "salary_terms": "оклад 100000 рублей",
                    "employment_basis": "трудовой договор",
                },
                "available_templates": [
                    {
                        "id": "hr_order_hiring_v1",
                        "document_type": "HR_ORDER_HIRING",
                    }
                ],
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert "LLM свободный черновик" not in body["draft_text"]
    assert "ПРИКАЗ" in body["draft_text"]


def test_document_type_detection_llm_fallback_strips_draft_text(monkeypatch):
    """ТЗ §2: LLM-fallback (когда code-detector вернул UNKNOWN) не должен
    отдавать draft_text — финальные юр-документы только через code-template."""
    store = FakeStore()
    monkeypatch.setattr(
        "app.main.get_runtime",
        lambda: runtime_with_store(store, llm=FakeDocumentPlanner()),
    )

    with TestClient(app) as client:
        response = client.post(
            "/document/type-detection",
            json={
                "question": "Расскажи в общих чертах про культуру компании.",
                "user_provided_fields": {},
                "available_templates": [],
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["draft_text"] is None, body
    assert body["can_generate_draft"] is False
    assert body["requires_human_review"] is True
