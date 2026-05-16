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

    def enqueue_review(self, **kwargs):
        self.review_queue.append(kwargs)
        return "review-1"


class FakeDocumentPlanner:
    enabled = True

    async def answer(self, question, results):
        return None

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
        return "Данных недостаточно. В предоставленных источниках нет нужных сведений."

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
