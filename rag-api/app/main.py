from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
import html
import json
from pathlib import Path
import time
from typing import Any, AsyncIterator

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .llm import MistralChatClient, MistralEmbeddingClient
from .rag import (
    AnswerPolicy,
    DocumentChunk,
    HybridRetriever,
    build_grounded_answer,
    confidence_from_results,
    split_text,
    tokenize,
)
from .settings import get_settings
from .storage import PostgresStore
from . import tg_copy
from .format_answer import confidence_band as compute_confidence_band
from .format_answer import format_answer as build_format_answer_parts
from .tg_format import format_docs as build_docs_summary_text
from .tg_format import format_history as build_history_text
from .multiturn import augment_retrieval_query, filter_relevant_prev_qas
from .tg_classifier import classify as classify_tg_update
from .tg_classifier import parse_allowed_ids


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Sprint 6 #5: graceful close singleton httpx clients на shutdown."""
    yield
    # `get_runtime` может быть @lru_cache функцией (prod) или lambda (tests via monkeypatch).
    # Не материализуем runtime если не было ни одного запроса — иначе создадим лишний инстанс.
    cache_info = getattr(get_runtime, "cache_info", None)
    if cache_info is None or cache_info().currsize > 0:
        runtime = get_runtime()
        for attr in ("llm", "embeddings"):
            closer = getattr(getattr(runtime, attr, None), "aclose", None)
            if callable(closer):
                await closer()


app = FastAPI(title="TestRag RAG API", version="0.1.0", lifespan=lifespan)


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
    debug: bool = False
    # Sprint 6 #7: Prev-N-QA augmentation (off by default; opt-in для multi-turn).
    prev_qa_count: int = Field(default=0, ge=0, le=5)


class Source(BaseModel):
    chunk_id: str
    file: str | None = None
    section: str | None = None
    date: str | None = None
    source_url: str | None = None
    score: float
    version: str | None = None
    effective_from: str | None = None
    effective_to: str | None = None
    status: str | None = None


class RetrievalDebugRow(BaseModel):
    chunk_id: str
    file: str | None = None
    section: str | None = None
    bm25_score: float
    normalized_bm25: float
    vector_score: float
    coverage: float
    section_boost: float
    final_score: float


class RetrievalDebug(BaseModel):
    query_tokens: list[str]
    weights: dict[str, float]
    has_vector: bool
    results: list[RetrievalDebugRow]


class AskResponse(BaseModel):
    request_log_id: str | None = None
    answer: str
    confidence: float
    # Sprint 8 #2 (codex-audit#5.2): banding в API чтобы UI/API парситли
    # из одной точки. Values: high|medium|low|none|unknown.
    confidence_band: str
    refused: bool
    request_type: str
    sources: list[Source]
    # Sprint 4 prep — formalized retrieval contract:
    status: str  # answerable | unanswerable | needs_human_review
    effective_date_max: str | None = None
    latency_ms: int | None = None
    # Sprint 6 #3 (codex-audit#6.3): retrieval explainability (opt-in via debug=true).
    debug: RetrievalDebug | None = None


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
    sample_files: list[str] = []


class CorpusSummaryResponse(BaseModel):
    categories: list[CorpusCategory]
    total_docs: int


class MetricsResponse(BaseModel):
    window_hours: int
    total_requests: int
    refusal_rate: float
    avg_latency_ms: float | None = None
    avg_confidence: float | None = None
    avg_prompt_tokens: float | None = None
    avg_completion_tokens: float | None = None
    bad_feedback_rate: float


class FollowupSource(BaseModel):
    chunk_id: str | None = None
    file: str | None = None
    section: str | None = None
    score: float | None = None


class FollowupResponse(BaseModel):
    question: str
    source: FollowupSource


class ExpandResponse(BaseModel):
    """Sprint 6 #6 N2 Quick-actions: full chunk content для «📖 Развернуть»."""
    text: str
    chunk_id: str | None = None
    file: str | None = None
    section: str | None = None
    source_url: str | None = None


class FormatAnswerSource(BaseModel):
    file: str | None = None
    chunk_id: str | None = None
    section: str | None = None
    score: float | None = None


class FormatAnswerRequest(BaseModel):
    """Sprint 8 #1 (issue #14): port n8n `Format Answer` JS → FastAPI.

    Принимает payload, тот же что собирался в n8n из выходов `Ask RAG API` +
    upstream `Whitelist` (chat_id, user_message_id). Возвращает массив
    готовых к sendMessage payload'ов (split, balance_tags, keyboard).
    """
    answer: str | None = None
    confidence: float | None = None
    refused: bool = False
    sources: list[FormatAnswerSource] = Field(default_factory=list)
    request_log_id: str = ""
    chat_id: int | str
    user_message_id: int | None = None


class FormatAnswerPart(BaseModel):
    chat_id: int | str
    text: str
    request_log_id: str = ""
    is_last: bool
    part_index: int
    part_total: int
    inline_keyboard: dict[str, Any] | None = None
    reply_to_message_id: int | None = None


class FormatAnswerResponse(BaseModel):
    parts: list[FormatAnswerPart]


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


def build_retrieval_debug(
    question: str,
    results: list[Any],
    query_embedding: list[float] | None,
) -> RetrievalDebug:
    """Sprint 6 #3 (codex-audit#6.3): retrieval breakdown для отладки/демо.

    Возвращает per-chunk decomposition (bm25/vector/coverage/section_boost) + текущие
    веса HybridRetriever + список query_tokens (показывает что отфильтровал tokenizer).
    """
    has_vector = query_embedding is not None and any(
        getattr(r.chunk, "embedding", None) for r in results
    )
    return RetrievalDebug(
        query_tokens=tokenize(question),
        weights={
            "bm25": HybridRetriever.BM25_WEIGHT,
            "vector": HybridRetriever.VECTOR_WEIGHT,
            "coverage_exp": HybridRetriever.COVERAGE_EXP,
            "section_boost_per_term": HybridRetriever.SECTION_BOOST_PER_TERM,
            "section_boost_max": HybridRetriever.SECTION_BOOST_MAX,
        },
        has_vector=has_vector,
        results=[
            RetrievalDebugRow(
                chunk_id=r.chunk.chunk_id,
                file=(r.chunk.metadata or {}).get("file"),
                section=(r.chunk.metadata or {}).get("section"),
                bm25_score=round(r.bm25_score, 4),
                normalized_bm25=round(r.normalized_bm25, 4),
                vector_score=round(r.vector_score, 4),
                coverage=round(r.coverage, 4),
                section_boost=round(r.section_boost, 4),
                final_score=round(r.final_score, 4),
            )
            for r in results
        ],
    )


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
                version=metadata.get("version"),
                effective_from=metadata.get("effective_from"),
                effective_to=metadata.get("effective_to"),
                status=metadata.get("status"),
            )
        )
    return sources


def derive_status(refused: bool, confidence: float, sources: list[Source]) -> str:
    """Formalized retrieval contract status. Sprint 4 prep (critique #1).

    - 'unanswerable': refused (no sources OR confidence below policy).
    - 'needs_human_review': low confidence on the upper edge (0.20-0.35) OR all sources в 'draft' status.
    - 'answerable': прошёл оба guard'а.
    """
    if refused:
        return "unanswerable"
    if confidence < 0.35 + 1e-6:
        return "needs_human_review"
    if sources and all((s.status or "active") == "draft" for s in sources):
        return "needs_human_review"
    return "answerable"


def latest_effective_date(sources: list[Source]) -> str | None:
    dates = [s.effective_from for s in sources if s.effective_from]
    return max(dates) if dates else None


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


class TelegramClassifyRequest(BaseModel):
    update: dict[str, Any]


class TelegramClassifyResponse(BaseModel):
    authorized: bool
    chat_id: int | None = None
    user_id: str
    text: str
    user_message_id: int | None = None
    event_type: str | None = None
    message_id: int | None = None
    rating: str | None = None
    category: str | None = None
    request_log_id: str | None = None
    followup_idx: int | None = None


class TelegramCopyResponse(BaseModel):
    key: str
    text: str


@app.post("/tg/classify", response_model=TelegramClassifyResponse)
def tg_classify(request: TelegramClassifyRequest) -> TelegramClassifyResponse:
    """Sprint 6 #1: бизнес-логика whitelist/routing из n8n Whitelist Code.

    n8n Whitelist node теперь — тонкий HttpRequest на этот endpoint.
    Это закрывает Issue #14 (n8n coupling) из kimi_audit и разрешает
    N8N_BLOCK_ENV_ACCESS_IN_NODE=true в docker-compose.
    """
    settings = get_settings()
    allowed = parse_allowed_ids(settings.allowed_telegram_user_ids_raw)
    result = classify_tg_update(request.update, allowed)
    return TelegramClassifyResponse(**result)


@app.get("/tg/copy/{key}", response_model=TelegramCopyResponse)
def tg_copy_get(key: str) -> TelegramCopyResponse:
    """Single point of edit для copy-блоков. Полезно для preview из n8n editor
    или smoke-тестов copy без re-importa workflow."""
    text = tg_copy.COPY_BLOCKS.get(key)
    if text is None:
        raise HTTPException(status_code=404, detail=f"Unknown copy key: {key}")
    return TelegramCopyResponse(key=key, text=text)


class FormatHistoryItem(BaseModel):
    id: str | None = None
    question: str | None = None
    answer: str | None = None
    confidence: float | None = None
    refused: bool = False
    created_at: str | None = None


class FormatHistoryRequest(BaseModel):
    items: list[FormatHistoryItem] = Field(default_factory=list)


class FormatTextResponse(BaseModel):
    text: str


class FormatDocsCategory(BaseModel):
    category: str | None = None
    label: str | None = None
    doc_count: int = 0
    sample_files: list[str] = Field(default_factory=list)


class FormatDocsRequest(BaseModel):
    categories: list[FormatDocsCategory] = Field(default_factory=list)
    total_docs: int = 0


@app.post("/tg/format-history", response_model=FormatTextResponse)
def tg_format_history(request: FormatHistoryRequest) -> FormatTextResponse:
    """Sprint 8 #2 (codex-audit#5.1): port n8n `Format History` JS → FastAPI.

    Принимает массив items из `/history`, возвращает готовый HTML-текст
    для Telegram sendMessage."""
    text = build_history_text([item.model_dump() for item in request.items])
    return FormatTextResponse(text=text)


@app.post("/tg/format-docs", response_model=FormatTextResponse)
def tg_format_docs(request: FormatDocsRequest) -> FormatTextResponse:
    """Sprint 8 #2 (codex-audit#5.1): port n8n `Format Docs` JS → FastAPI."""
    text = build_docs_summary_text(
        [c.model_dump() for c in request.categories],
        request.total_docs,
    )
    return FormatTextResponse(text=text)


@app.post("/tg/format-answer", response_model=FormatAnswerResponse)
def tg_format_answer(request: FormatAnswerRequest) -> FormatAnswerResponse:
    """Sprint 8 #1 (issue #14): port n8n `Format Answer` JS → FastAPI.

    Заменяет 158-строчный JS Code node на n8n. Workflow обновится отдельно
    (HTTP Request на этот endpoint вместо Code), до миграции существующий
    JS-узел остаётся (двухтрактовое покрытие). См. `tests/test_format_answer.py`
    для parity-coverage против JS-копии.
    """
    parts = build_format_answer_parts(
        answer=request.answer,
        confidence=request.confidence,
        refused=request.refused,
        sources=[s.model_dump(exclude_none=True) for s in request.sources],
        request_log_id=request.request_log_id,
        chat_id=request.chat_id,
        user_message_id=request.user_message_id,
    )
    return FormatAnswerResponse(parts=[FormatAnswerPart(**p) for p in parts])


@app.get("/health")
def health() -> dict[str, Any]:
    runtime = get_runtime()
    settings = get_settings()
    return {
        "status": "ok",
        "chunk_count": len(runtime.chunks),
        "mistral_enabled": runtime.llm.enabled,
        "embeddings_enabled": runtime.embeddings.enabled,
        "postgres_enabled": runtime.store.enabled,
        # Sprint 8 #2 (codex-audit#6.3): покажи активные corpus + manifest paths,
        # чтобы оператор сразу увидел, что подгружен (sample_docs vs corpus) и
        # был ли применён manifest. Раньше mismatched volume mounts можно было
        # обнаружить только через chunk_count drift.
        "docs_path": str(settings.docs_path),
        "docs_manifest_path": (
            str(settings.docs_manifest_path) if settings.docs_manifest_path else None
        ),
        "min_confidence": settings.min_confidence,
    }


@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest) -> AskResponse:
    runtime = get_runtime()
    t0 = time.perf_counter()
    # Sprint 6 #7: Prev-N-QA augmentation. LLM prompt остаётся на current question
    # (см. ниже), augmented строка идёт ТОЛЬКО в retrieval (embedding + BM25).
    retrieval_query = request.question
    if request.prev_qa_count > 0 and request.telegram_user_id:
        recent = runtime.store.recent_requests(
            telegram_user_id=request.telegram_user_id, limit=request.prev_qa_count + 1
        )
        # Первый элемент — текущий же запрос (если уже залогирован), пропускаем
        prev = [r for r in recent if r.get("question") != request.question]
        prev = filter_relevant_prev_qas(prev, skip_refused=True)
        retrieval_query = augment_retrieval_query(
            request.question, prev, max_prev=request.prev_qa_count
        )
    query_embedding = await runtime.embeddings.embed_query(retrieval_query)
    results = runtime.retriever.search(retrieval_query, top_k=request.top_k, query_embedding=query_embedding)
    confidence = confidence_from_results(results)
    sources = to_sources(results)
    request_type = classify_request(request.question)

    refused = not runtime.policy.can_answer(confidence=confidence, source_count=len(sources))
    usage: dict[str, Any] = {"model": None, "prompt_tokens": None, "completion_tokens": None}
    if refused:
        answer = "Не хватает надежных источников для ответа. Уточните вопрос или добавьте документ в базу знаний."
    else:
        mistral_answer, usage = await runtime.llm.answer(request.question, results)
        answer = mistral_answer or build_grounded_answer(request.question, results)
        if mistral_answer and is_pure_refusal(mistral_answer):
            refused = True
            confidence = 0.0

    latency_ms = int((time.perf_counter() - t0) * 1000)
    status = derive_status(refused, confidence, sources)
    request_log_id = runtime.store.log_request(
        telegram_user_id=request.telegram_user_id,
        question=request.question,
        request_type=request_type,
        confidence=round(confidence, 4),
        refused=refused,
        answer=answer,
        sources=[source.model_dump() for source in sources],
        latency_ms=latency_ms,
        llm_model=usage.get("model"),
        prompt_tokens=usage.get("prompt_tokens"),
        completion_tokens=usage.get("completion_tokens"),
    )
    debug = build_retrieval_debug(request.question, results, query_embedding) if request.debug else None
    return AskResponse(
        request_log_id=request_log_id,
        answer=answer,
        confidence=round(confidence, 4),
        confidence_band=compute_confidence_band(0.0 if refused else confidence),
        refused=refused,
        request_type=request_type,
        sources=sources,
        status=status,
        effective_date_max=latest_effective_date(sources),
        latency_ms=latency_ms,
        debug=debug,
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
        context: list[dict[str, Any]] = []
        if request.category == "human" and request.telegram_user_id:
            context = runtime.store.recent_requests(
                telegram_user_id=request.telegram_user_id,
                limit=5,
            )
        runtime.store.enqueue_review(
            request_log_id=request.request_log_id,
            reason=request.category or request.comment or "bad_feedback",
            context=context,
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


@app.get("/followup", response_model=FollowupResponse)
def followup(request_log_id: str, idx: int = 0) -> FollowupResponse:
    if not request_log_id:
        raise HTTPException(status_code=400, detail="request_log_id required")
    if idx < 0 or idx > 9:
        raise HTTPException(status_code=400, detail="idx must be in [0, 9]")
    runtime = get_runtime()
    source = runtime.store.get_request_source(request_log_id, idx)
    if not source:
        raise HTTPException(status_code=404, detail="source not found")
    section = (source.get("section") or "").strip()
    file_name = (source.get("file") or "").strip()
    if section and file_name:
        question = f"Расскажи подробнее про раздел «{section}» из документа {file_name}."
    elif section:
        question = f"Расскажи подробнее про раздел «{section}»."
    elif file_name:
        question = f"Расскажи подробнее про документ {file_name}."
    else:
        question = "Расскажи подробнее про этот источник."
    return FollowupResponse(
        question=question,
        source=FollowupSource(
            chunk_id=source.get("chunk_id"),
            file=source.get("file"),
            section=source.get("section"),
            score=source.get("score"),
        ),
    )


@app.post("/clarify", response_model=AskResponse)
async def clarify(request_log_id: str) -> AskResponse:
    """Sprint 6 #6 (N2 Quick-actions): «🔁 Уточнить» rerun на оригинальный вопрос
    с расширенным top_k=10 для более глубокого поиска. Возвращает новый
    AskResponse как обычный /ask, с новым request_log_id."""
    if not request_log_id:
        raise HTTPException(status_code=400, detail="request_log_id required")
    runtime = get_runtime()
    question = runtime.store.get_request_question(request_log_id)
    if not question:
        raise HTTPException(status_code=404, detail="request_log not found")
    return await ask(AskRequest(question=question, telegram_user_id=None, top_k=10))


@app.get("/expand", response_model=ExpandResponse)
def expand(request_log_id: str, idx: int = 0) -> ExpandResponse:
    """Sprint 6 #6 (N2 Quick-actions): «📖 Развернуть» — полный текст top-N
    источника. Возвращает full chunk content (не snippet) для конкретного
    индекса из request_log.sources."""
    if not request_log_id:
        raise HTTPException(status_code=400, detail="request_log_id required")
    if idx < 0 or idx > 9:
        raise HTTPException(status_code=400, detail="idx must be in [0, 9]")
    runtime = get_runtime()
    source = runtime.store.get_request_source(request_log_id, idx)
    if not source:
        raise HTTPException(status_code=404, detail="source not found")
    chunk_id = source.get("chunk_id")
    chunk = next((c for c in runtime.chunks if c.chunk_id == chunk_id), None)
    if chunk is None:
        raise HTTPException(status_code=404, detail="chunk not found in current index")
    file_name = source.get("file") or "(без имени файла)"
    section = source.get("section") or ""
    # Telegram parse_mode=HTML: чанк может содержать `<` (markdown autolinks
    # `<https://...>` в корпусе normative-источников), `&` (M&A, P&L) — без
    # escape sendMessage отдаёт 400 "can't parse entities".
    safe_file = html.escape(file_name)
    safe_section = html.escape(section)
    safe_content = html.escape(chunk.content)
    header_section = f" · {safe_section}" if safe_section else ""
    text = f"📖 <code>{safe_file}</code>{header_section}\n\n{safe_content}"
    return ExpandResponse(
        text=text,
        chunk_id=chunk_id,
        file=source.get("file"),
        section=source.get("section"),
        source_url=chunk.metadata.get("source_url"),
    )


@app.get("/metrics", response_model=MetricsResponse)
def metrics(window_hours: int = 168) -> MetricsResponse:
    if window_hours <= 0 or window_hours > 24 * 90:
        raise HTTPException(status_code=400, detail="window_hours must be in (0, 2160]")
    runtime = get_runtime()
    raw = runtime.store.metrics(window_hours=window_hours)
    return MetricsResponse(**raw)


@app.get("/docs/summary", response_model=CorpusSummaryResponse)
def docs_summary() -> CorpusSummaryResponse:
    runtime = get_runtime()
    rows = runtime.store.corpus_summary()
    categories = [
        CorpusCategory(
            category=row["category"],
            label=CORPUS_CATEGORY_LABELS.get(row["category"], row["category"]),
            doc_count=row["doc_count"],
            sample_files=row.get("sample_files", []),
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
