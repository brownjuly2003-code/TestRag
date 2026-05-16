from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .llm import MistralChatClient, MistralEmbeddingClient
from .rag import (
    AnswerPolicy,
    DocumentChunk,
    HybridRetriever,
    build_grounded_answer,
    confidence_from_results,
)
from .settings import get_settings
from .storage import PostgresStore


app = FastAPI(title="TestRag RAG API", version="0.1.0")


@dataclass(frozen=True)
class Runtime:
    chunks: list[DocumentChunk]
    retriever: HybridRetriever
    policy: AnswerPolicy
    llm: MistralChatClient
    embeddings: MistralEmbeddingClient
    store: PostgresStore


class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    telegram_user_id: str | None = None
    top_k: int = Field(default=5, ge=1, le=10)


class Source(BaseModel):
    chunk_id: str
    file: str | None = None
    section: str | None = None
    date: str | None = None
    source_url: str | None = None
    score: float


class AskResponse(BaseModel):
    request_log_id: str | None = None
    answer: str
    confidence: float
    refused: bool
    request_type: str
    sources: list[Source]


class FeedbackRequest(BaseModel):
    request_log_id: str | None = None
    telegram_user_id: str | None = None
    rating: str
    comment: str | None = None
    category: str | None = None
    free_text: str | None = None


class HistoryItem(BaseModel):
    id: str
    question: str
    answer: str | None = None
    confidence: float | None = None
    refused: bool
    created_at: str | None = None


class HistoryResponse(BaseModel):
    items: list[HistoryItem]


class CorpusCategory(BaseModel):
    category: str
    label: str
    doc_count: int


class CorpusSummaryResponse(BaseModel):
    categories: list[CorpusCategory]
    total_docs: int


CORPUS_CATEGORY_LABELS: dict[str, str] = {
    "01_hr_pol": "HR — политики и регламенты",
    "02_hr_tpl": "HR — шаблоны кадровых документов",
    "03_legal_con": "Legal — договоры",
    "04_legal_cla": "Legal — претензии и иски",
    "05_tlog": "T&L — транспорт и логистика",
    "06_comp": "Compliance — комплаенс",
    "07_faq": "FAQ — частые вопросы",
    "other": "Прочее",
}


class RequiredField(BaseModel):
    name: str
    label: str
    required: bool
    value: Any = None
    source: str


class DocumentSource(BaseModel):
    file: str | None = None
    section: str | None = None
    date: str | None = None
    quote_or_summary: str


class DocumentTypeRequest(BaseModel):
    question: str = Field(min_length=1)
    user_provided_fields: dict[str, Any] = Field(default_factory=dict)
    available_templates: list[dict[str, Any]] = Field(default_factory=list)
    top_k: int = Field(default=5, ge=1, le=10)


class DocumentTypeResponse(BaseModel):
    intent: str
    document_type: str
    document_type_label: str
    confidence: str
    can_generate_draft: bool
    requires_human_review: bool
    reasoning: str
    required_fields: list[RequiredField]
    missing_fields: list[str]
    risk_flags: list[str]
    source_requirements: list[str]
    draft_outline: list[str]
    draft_text: str | None
    sources: list[DocumentSource]
    user_message: str


DOCUMENT_SYSTEM_PROMPT = """Ты AI-ассистент юридического и HR-отдела. Ты работаешь в RAG-системе поверх базы документов компании, шаблонов и нормативных источников.

Определи intent, тип юридического/HR-документа, confidence, недостающие поля и возможность подготовки черновика. Не создавай финальный юридически значимый документ без утвержденного шаблона и источников. Верни строго JSON по схеме из docs/legal-document-prompts.md."""


DOCUMENT_TYPES: dict[str, dict[str, Any]] = {
    "HR_ORDER_HIRING": {
        "label": "Приказ о приеме на работу",
        "keywords": ["приказ", "прием", "приём", "принять", "трудоустрой"],
        "required_fields": {
            "employee_full_name": "ФИО работника",
            "position": "Должность",
            "department": "Подразделение",
            "start_date": "Дата начала работы",
            "salary_terms": "Условия оплаты",
            "employment_basis": "Основание оформления",
        },
        "outline": ["Реквизиты приказа", "Данные работника", "Условия приема", "Основание", "Подписи"],
    },
    "HR_ORDER_VACATION": {
        "label": "Приказ о предоставлении отпуска",
        "keywords": ["приказ", "отпуск"],
        "required_fields": {
            "employee_full_name": "ФИО работника",
            "vacation_start_date": "Дата начала отпуска",
            "vacation_end_date": "Дата окончания отпуска",
            "vacation_basis": "Основание отпуска",
        },
        "outline": ["Реквизиты приказа", "Период отпуска", "Основание", "Подписи"],
    },
    "HR_ORDER_TERMINATION": {
        "label": "Приказ об увольнении",
        "keywords": ["приказ", "увольнен", "увольнение", "расторг"],
        "required_fields": {
            "employee_full_name": "ФИО работника",
            "termination_date": "Дата увольнения",
            "termination_basis": "Основание увольнения",
        },
        "outline": ["Реквизиты приказа", "Данные работника", "Основание увольнения", "Подписи"],
    },
    "HR_ADDITIONAL_AGREEMENT": {
        "label": "Дополнительное соглашение к трудовому договору",
        "keywords": ["дополнительное соглашение", "допсоглашение", "трудовой договор"],
        "required_fields": {
            "employee_full_name": "ФИО работника",
            "contract_number": "Номер трудового договора",
            "change_description": "Описание изменений",
            "effective_date": "Дата вступления изменений в силу",
        },
        "outline": ["Стороны", "Изменяемые условия", "Дата вступления", "Подписи"],
    },
    "HR_EMPLOYMENT_CONTRACT_DRAFT": {
        "label": "Черновик трудового договора",
        "keywords": ["трудовой договор", "договор с работником"],
        "required_fields": {
            "employee_full_name": "ФИО работника",
            "position": "Должность",
            "department": "Подразделение",
            "start_date": "Дата начала работы",
            "salary_terms": "Условия оплаты",
        },
        "outline": ["Стороны", "Трудовая функция", "Оплата", "Режим работы", "Права и обязанности"],
    },
    "HR_JOB_DESCRIPTION": {
        "label": "Должностная инструкция",
        "keywords": ["должностная инструкция", "обязанности должности"],
        "required_fields": {
            "position": "Должность",
            "department": "Подразделение",
            "responsibilities": "Должностные обязанности",
        },
        "outline": ["Общие положения", "Обязанности", "Права", "Ответственность"],
    },
    "HR_POLICY_NOTICE": {
        "label": "Уведомление работника",
        "keywords": ["уведомление", "уведомить работника"],
        "required_fields": {
            "employee_full_name": "ФИО работника",
            "notice_subject": "Предмет уведомления",
            "notice_date": "Дата уведомления",
        },
        "outline": ["Адресат", "Предмет уведомления", "Сроки", "Подпись"],
    },
    "LEGAL_SERVICE_CONTRACT": {
        "label": "Договор оказания услуг",
        "keywords": ["договор оказания услуг", "услуги"],
        "required_fields": {
            "counterparty": "Контрагент",
            "services": "Перечень услуг",
            "price_terms": "Стоимость и порядок оплаты",
            "term": "Срок договора",
        },
        "outline": ["Стороны", "Предмет", "Стоимость", "Срок", "Ответственность"],
    },
    "LEGAL_SUPPLY_CONTRACT": {
        "label": "Договор поставки",
        "keywords": ["договор поставки", "поставка"],
        "required_fields": {
            "counterparty": "Контрагент",
            "goods": "Товары",
            "delivery_terms": "Условия поставки",
            "price_terms": "Стоимость и порядок оплаты",
        },
        "outline": ["Стороны", "Предмет поставки", "Сроки", "Оплата", "Ответственность"],
    },
    "LEGAL_NDA": {
        "label": "Соглашение о конфиденциальности",
        "keywords": ["nda", "конфиденциальност", "неразглашен"],
        "required_fields": {
            "counterparty": "Контрагент",
            "confidential_information": "Конфиденциальная информация",
            "term": "Срок действия",
        },
        "outline": ["Стороны", "Конфиденциальная информация", "Обязанности", "Срок"],
    },
    "LEGAL_POWER_OF_ATTORNEY": {
        "label": "Доверенность",
        "keywords": ["доверенность", "полномоч"],
        "required_fields": {
            "representative_full_name": "ФИО представителя",
            "powers": "Полномочия",
            "valid_until": "Срок действия",
        },
        "outline": ["Доверитель", "Представитель", "Полномочия", "Срок"],
    },
    "LEGAL_CLAIM_LETTER": {
        "label": "Претензия контрагенту",
        "keywords": ["претенз", "нарушен", "просроч", "контрагент"],
        "required_fields": {
            "counterparty": "Контрагент",
            "contract_number": "Номер договора",
            "contract_date": "Дата договора",
            "breach_description": "Описание нарушения",
            "claim_amount": "Сумма требования",
            "deadline": "Срок исполнения требования",
            "legal_basis": "Правовое основание",
        },
        "outline": ["Адресат", "Обстоятельства нарушения", "Требования", "Срок ответа", "Приложения"],
    },
    "LEGAL_RESPONSE_LETTER": {
        "label": "Ответ на претензию или запрос",
        "keywords": ["ответ на претензию", "ответ на запрос"],
        "required_fields": {
            "incoming_request": "Входящий запрос",
            "position": "Позиция компании",
            "legal_basis": "Правовое основание",
        },
        "outline": ["Реквизиты обращения", "Позиция", "Обоснование", "Приложения"],
    },
    "LEGAL_INTERNAL_MEMO": {
        "label": "Внутренняя юридическая справка",
        "keywords": ["юридическая справка", "мемо", "правовая позиция"],
        "required_fields": {
            "topic": "Тема справки",
            "facts": "Фактические обстоятельства",
            "questions": "Правовые вопросы",
        },
        "outline": ["Вопрос", "Факты", "Анализ", "Риски", "Вывод"],
    },
}


def split_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[str]:
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = max(0, end - chunk_overlap)
    return chunks


def detect_section(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("#"):
            return line.strip("# ").strip()
    return None


def load_sample_chunks(docs_path: Path, manifest_path: Path | None = None) -> list[DocumentChunk]:
    if not docs_path.exists():
        return []

    chunks: list[DocumentChunk] = []
    for file_path in _iter_document_files(docs_path, manifest_path):
        text = file_path.read_text(encoding="utf-8")
        section = detect_section(text)
        for index, chunk_text in enumerate(split_text(text)):
            chunks.append(
                DocumentChunk(
                    chunk_id=f"{file_path.stem}:{index}",
                    content=chunk_text,
                    metadata={
                        "file": file_path.name,
                        "section": section,
                        "date": "2026-05-15",
                        "source_url": "",
                        "document_type": "demo",
                    },
                )
            )
    return chunks


def _iter_document_files(docs_path: Path, manifest_path: Path | None = None) -> list[Path]:
    if not manifest_path:
        return sorted(docs_path.glob("*.md"))
    if not manifest_path.exists():
        return []

    root_path = docs_path.resolve()
    files = []
    seen = set()
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        entry = line.strip()
        if not entry or entry.startswith("#"):
            continue
        file_path = (root_path / entry).resolve()
        if file_path in seen:
            continue
        if file_path.suffix.lower() != ".md" or not file_path.is_file():
            continue
        if not file_path.is_relative_to(root_path):
            continue
        files.append(file_path)
        seen.add(file_path)
    return files


@lru_cache
def get_runtime() -> Runtime:
    settings = get_settings()
    llm = MistralChatClient(settings.mistral_api_key, settings.mistral_chat_model)
    embeddings = MistralEmbeddingClient(settings.mistral_api_key, settings.mistral_embedding_model)
    store = PostgresStore(settings.database_url)
    if store.enabled:
        store.ingest_documents(settings.docs_path, embeddings, settings.docs_manifest_path)
    chunks = store.load_chunks() if store.enabled else []
    if not chunks:
        chunks = load_sample_chunks(settings.docs_path, settings.docs_manifest_path)
    return Runtime(
        chunks=chunks,
        retriever=HybridRetriever(chunks),
        policy=AnswerPolicy(min_confidence=settings.min_confidence),
        llm=llm,
        embeddings=embeddings,
        store=store,
    )


def classify_request(question: str) -> str:
    normalized = question.lower()
    if any(marker in normalized for marker in ["приказ", "шаблон", "договор", "соглашение"]):
        return "template_draft"
    if any(marker in normalized for marker in ["тк", "работ", "отпуск", "испытан", "увольнен"]):
        return "hr"
    if any(marker in normalized for marker in ["закон", "статья", "норма", "договор"]):
        return "legal"
    return "unknown"


def detect_document_type(question: str) -> str:
    normalized = question.lower()
    best_type = "UNKNOWN"
    best_score = 0
    for document_type, config in DOCUMENT_TYPES.items():
        score = sum(1 for keyword in config["keywords"] if keyword in normalized)
        if score > best_score:
            best_type = document_type
            best_score = score
    return best_type


def build_document_type_response(
    request: DocumentTypeRequest,
    sources: list[DocumentSource],
) -> DocumentTypeResponse:
    document_type = detect_document_type(request.question)
    config = DOCUMENT_TYPES.get(document_type)
    if not config:
        return DocumentTypeResponse(
            intent="document_type_detection",
            document_type="UNKNOWN",
            document_type_label="Тип не определен",
            confidence="LOW",
            can_generate_draft=False,
            requires_human_review=True,
            reasoning="В запросе не найдено устойчивых признаков разрешенных типов документов MVP.",
            required_fields=[],
            missing_fields=[],
            risk_flags=["Тип документа не определен"],
            source_requirements=["Уточнить тип документа и добавить утвержденный шаблон"],
            draft_outline=[],
            draft_text=None,
            sources=sources,
            user_message="Не удалось уверенно определить тип документа. Уточните, какой документ нужно подготовить.",
        )

    required_fields = []
    missing_fields = []
    for field_name, label in config["required_fields"].items():
        value = request.user_provided_fields.get(field_name)
        source = "user" if value not in (None, "") else "missing"
        if source == "missing":
            missing_fields.append(field_name)
        required_fields.append(
            RequiredField(
                name=field_name,
                label=label,
                required=True,
                value=value,
                source=source,
            )
        )

    has_template = any(template.get("document_type") == document_type for template in request.available_templates)
    confidence = "HIGH" if not missing_fields and sources and has_template else "MEDIUM"
    can_generate_draft = confidence == "HIGH"
    if not sources:
        confidence = "MEDIUM" if not missing_fields else "LOW"
        can_generate_draft = False

    source_requirements = []
    if not sources:
        source_requirements.append("Нужны релевантные источники RAG или утвержденный шаблон документа")
    if not has_template:
        source_requirements.append("Нужен утвержденный шаблон для выбранного типа документа")
    if can_generate_draft and document_type != "HR_ORDER_HIRING":
        can_generate_draft = False
        confidence = "MEDIUM"
        source_requirements.append("Для этого типа документа пока нет кодового шаблона MVP")

    risk_flags = ["Требуется ручная проверка юристом/HR"]
    if missing_fields:
        risk_flags.append("Не заполнены обязательные поля")
    draft_text = None
    if can_generate_draft and document_type == "HR_ORDER_HIRING":
        fields = request.user_provided_fields
        draft_text = (
            "Требует проверки юристом/HR\n\n"
            "ПРИКАЗ\n"
            "о приеме на работу\n\n"
            f"Принять на работу: {fields['employee_full_name']}.\n"
            f"Должность: {fields['position']}.\n"
            f"Подразделение: {fields['department']}.\n"
            f"Дата начала работы: {fields['start_date']}.\n"
            f"Условия оплаты: {fields['salary_terms']}.\n"
            f"Основание оформления: {fields['employment_basis']}.\n\n"
            "Ответственный специалист должен проверить реквизиты, основание оформления и применимый шаблон до подписания.\n\n"
            "Документ является черновиком и требует проверки ответственным специалистом."
        )

    return DocumentTypeResponse(
        intent="template_draft" if any(word in request.question.lower() for word in ["сделай", "подготов", "черновик"]) else "document_type_detection",
        document_type=document_type,
        document_type_label=config["label"],
        confidence=confidence,
        can_generate_draft=can_generate_draft,
        requires_human_review=True,
        reasoning=f"Запрос соответствует типу: {config['label']}.",
        required_fields=required_fields,
        missing_fields=missing_fields,
        risk_flags=risk_flags,
        source_requirements=source_requirements,
        draft_outline=config["outline"],
        draft_text=draft_text,
        sources=sources,
        user_message=(
            "Тип документа определен, но для черновика нужно заполнить обязательные поля."
            if missing_fields
            else "Черновик подготовлен по утвержденному шаблону MVP и требует проверки юристом/HR."
            if draft_text
            else "Тип документа определен. Перед выдачей черновика проверьте шаблон и источники."
        ),
    )


def build_document_user_prompt(
    request: DocumentTypeRequest,
    sources: list[DocumentSource],
) -> str:
    return "\n\n".join(
        [
            f"Запрос пользователя:\n{request.question}",
            "Данные пользователя:\n" + json.dumps(request.user_provided_fields, ensure_ascii=False),
            "Найденные источники RAG:\n" + json.dumps([source.model_dump() for source in sources], ensure_ascii=False),
            "Доступные шаблоны:\n" + json.dumps(request.available_templates, ensure_ascii=False),
            f"Текущая дата:\n{date.today().isoformat()}",
            "Определи intent, тип документа, confidence, недостающие поля и возможность подготовки черновика. Верни строго JSON.",
        ]
    )


REFUSAL_PREFIXES = ("данных недостаточно", "не хватает", "не нашел", "не нашёл")


def is_pure_refusal(mistral_answer: str, min_body_chars: int = 120) -> bool:
    """Return True only if mistral_answer is a refusal phrase without substantive body.

    Mistral often leads useful aviation-grounded answers with «Данных недостаточно...»
    as a cautious preface, then provides actual content from sources. We treat such
    answers as valid (not a refusal). True refusal = first sentence is a refusal phrase
    AND the remainder is shorter than ``min_body_chars``.
    """
    stripped = mistral_answer.strip()
    if not stripped.lower().startswith(REFUSAL_PREFIXES):
        return False
    positions = [stripped.find(p) for p in (".", "!", "?")]
    positions = [p for p in positions if p >= 0]
    first_sentence_end = min(positions) if positions else -1
    body = stripped[first_sentence_end + 1 :].strip() if first_sentence_end >= 0 else ""
    return len(body) < min_body_chars


def to_sources(results: list[Any]) -> list[Source]:
    sources = []
    for result in results:
        if result.final_score <= 0:
            continue
        metadata = result.chunk.metadata
        sources.append(
            Source(
                chunk_id=result.chunk.chunk_id,
                file=metadata.get("file"),
                section=metadata.get("section"),
                date=metadata.get("date"),
                source_url=metadata.get("source_url"),
                score=round(result.final_score, 4),
            )
        )
    return sources


def to_document_sources(results: list[Any]) -> list[DocumentSource]:
    sources = []
    for result in results:
        if result.final_score <= 0:
            continue
        metadata = result.chunk.metadata
        snippet = result.chunk.content.strip().replace("\n", " ")
        if len(snippet) > 240:
            snippet = snippet[:237].rstrip() + "..."
        sources.append(
            DocumentSource(
                file=metadata.get("file"),
                section=metadata.get("section"),
                date=metadata.get("date"),
                quote_or_summary=snippet,
            )
        )
    return sources


@app.get("/health")
def health() -> dict[str, Any]:
    runtime = get_runtime()
    return {
        "status": "ok",
        "chunk_count": len(runtime.chunks),
        "mistral_enabled": runtime.llm.enabled,
        "embeddings_enabled": runtime.embeddings.enabled,
        "postgres_enabled": runtime.store.enabled,
    }


@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest) -> AskResponse:
    runtime = get_runtime()
    query_embedding = await runtime.embeddings.embed_query(request.question)
    results = runtime.retriever.search(request.question, top_k=request.top_k, query_embedding=query_embedding)
    confidence = confidence_from_results(results)
    sources = to_sources(results)
    request_type = classify_request(request.question)

    refused = not runtime.policy.can_answer(confidence=confidence, source_count=len(sources))
    if refused:
        answer = "Не хватает надежных источников для ответа. Уточните вопрос или добавьте документ в базу знаний."
    else:
        mistral_answer = await runtime.llm.answer(request.question, results)
        answer = mistral_answer or build_grounded_answer(request.question, results)
        if mistral_answer and is_pure_refusal(mistral_answer):
            refused = True
            confidence = 0.0

    request_log_id = runtime.store.log_request(
        telegram_user_id=request.telegram_user_id,
        question=request.question,
        request_type=request_type,
        confidence=round(confidence, 4),
        refused=refused,
        answer=answer,
        sources=[source.model_dump() for source in sources],
    )
    return AskResponse(
        request_log_id=request_log_id,
        answer=answer,
        confidence=round(confidence, 4),
        refused=refused,
        request_type=request_type,
        sources=sources,
    )


@app.post("/feedback")
def feedback(request: FeedbackRequest) -> dict[str, str]:
    if request.rating not in {"good", "bad"}:
        raise HTTPException(status_code=400, detail="rating must be good or bad")
    runtime = get_runtime()
    runtime.store.log_feedback(
        request_log_id=request.request_log_id,
        telegram_user_id=request.telegram_user_id,
        rating=request.rating,
        comment=request.comment,
        category=request.category,
        free_text=request.free_text,
    )
    if request.rating == "bad":
        runtime.store.enqueue_review(
            request_log_id=request.request_log_id,
            reason=request.category or request.comment or "bad_feedback",
        )
    return {"status": "accepted"}


@app.get("/history", response_model=HistoryResponse)
def history(telegram_user_id: str, limit: int = 5) -> HistoryResponse:
    if not telegram_user_id:
        raise HTTPException(status_code=400, detail="telegram_user_id required")
    limit = max(1, min(limit, 20))
    runtime = get_runtime()
    items = runtime.store.recent_requests(telegram_user_id=telegram_user_id, limit=limit)
    return HistoryResponse(items=[HistoryItem(**row) for row in items])


@app.get("/docs/summary", response_model=CorpusSummaryResponse)
def docs_summary() -> CorpusSummaryResponse:
    runtime = get_runtime()
    rows = runtime.store.corpus_summary()
    categories = [
        CorpusCategory(
            category=row["category"],
            label=CORPUS_CATEGORY_LABELS.get(row["category"], row["category"]),
            doc_count=row["doc_count"],
        )
        for row in rows
    ]
    return CorpusSummaryResponse(
        categories=categories,
        total_docs=sum(c.doc_count for c in categories),
    )


@app.post("/document/type-detection", response_model=DocumentTypeResponse)
async def document_type_detection(request: DocumentTypeRequest) -> DocumentTypeResponse:
    runtime = get_runtime()
    query_embedding = await runtime.embeddings.embed_query(request.question)
    results = runtime.retriever.search(request.question, top_k=request.top_k, query_embedding=query_embedding)
    sources = to_document_sources(results)
    safe_response = build_document_type_response(request, sources)
    if safe_response.document_type != "UNKNOWN":
        return safe_response

    mistral_response = await runtime.llm.document_plan(
        DOCUMENT_SYSTEM_PROMPT,
        build_document_user_prompt(request, sources),
    )
    if mistral_response:
        return DocumentTypeResponse.model_validate(mistral_response)

    return build_document_type_response(request, sources)
