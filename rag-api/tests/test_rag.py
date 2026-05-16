from app.rag import AnswerPolicy, DocumentChunk, HybridRetriever, confidence_from_results
from pathlib import Path


def test_hybrid_retriever_prefers_exact_legal_term_match():
    chunks = [
        DocumentChunk(
            chunk_id="vacation",
            content="Ежегодный оплачиваемый отпуск предоставляется работнику по графику отпусков.",
            metadata={"file": "hr_policy.md", "section": "Отпуска", "date": "2026-01-10"},
        ),
        DocumentChunk(
            chunk_id="probation",
            content="Статья 70 ТК РФ регулирует испытание при приеме на работу и срок испытания.",
            metadata={"file": "labor_code_notes.md", "section": "Испытание", "date": "2026-01-10"},
        ),
    ]

    retriever = HybridRetriever(chunks)
    results = retriever.search("статья 70 испытание при приеме на работу", top_k=2)

    assert results[0].chunk.chunk_id == "probation"
    assert results[0].bm25_score > 0
    assert results[0].final_score > results[1].final_score


def test_answer_policy_requires_source_and_confidence():
    policy = AnswerPolicy(min_confidence=0.35)

    assert policy.can_answer(confidence=0.7, source_count=1) is True
    assert policy.can_answer(confidence=0.2, source_count=1) is False
    assert policy.can_answer(confidence=0.9, source_count=0) is False


def test_hybrid_retriever_does_not_overtrust_single_generic_term_with_embeddings():
    chunks = [
        DocumentChunk(
            chunk_id="vacation",
            content="Локальные правила согласования отпусков описывают график ежегодного отпуска.",
            metadata={"file": "vacation_policy.md"},
            embedding=[1.0, 0.0],
        ),
        DocumentChunk(
            chunk_id="probation",
            content="Статья 70 ТК РФ регулирует испытание при приеме на работу.",
            metadata={"file": "labor_code_notes.md"},
            embedding=[0.0, 1.0],
        ),
    ]

    retriever = HybridRetriever(chunks)
    results = retriever.search(
        "какие правила перевозки лития морем",
        top_k=2,
        query_embedding=[1.0, 0.0],
    )

    assert confidence_from_results(results) < 0.35


def test_hybrid_retriever_matches_russian_inflected_domain_terms():
    chunks = [
        DocumentChunk(
            chunk_id="hr-template",
            content="Шаблон содержит обязательные реквизиты работника и условия трудового договора.",
            metadata={"file": "employment_order.md"},
        ),
        DocumentChunk(
            chunk_id="waybill",
            content="Порядок оформления путевых листов: путевой лист, водитель, маршрут и обязательные поля рейса.",
            metadata={"file": "waybill.md"},
        ),
    ]

    retriever = HybridRetriever(chunks)
    results = retriever.search("Какие обязательные реквизиты путевого листа?", top_k=2)

    assert results[0].chunk.chunk_id == "waybill"
    assert confidence_from_results(results) >= 0.35


def test_confidence_stays_low_when_specific_terms_are_missing():
    chunks = [
        DocumentChunk(
            chunk_id="dangerous-goods",
            content="Правила перевозки опасных грузов автомобильным транспортом по ADR.",
            metadata={"file": "dangerous_goods.md"},
        ),
        DocumentChunk(
            chunk_id="road-transport",
            content="Договор автомобильной перевозки груза описывает общие правила перевозки.",
            metadata={"file": "road_transport.md"},
        ),
    ]

    retriever = HybridRetriever(chunks)
    results = retriever.search("Какие правила перевозки лития морем?", top_k=2)

    assert confidence_from_results(results) < 0.35


def test_probation_corpus_says_extension_is_not_allowed():
    corpus_path = Path(__file__).resolve().parents[2] / "corpus" / "01_hr_probation_procedure.md"
    text = corpus_path.read_text(encoding="utf-8").lower()

    assert "продление испытательного срока не допускается" in text
    assert "продление.** допускается" not in text


def test_aviation_profile_in_hr_probation():
    corpus_path = Path(__file__).resolve().parents[2] / "corpus" / "01_hr_probation_procedure.md"
    text = corpus_path.read_text(encoding="utf-8").lower()

    assert "допуск" in text or "пропуск" in text
    assert "контролируем" in text or "терминал" in text or "аэропорт" in text


def test_aviation_profile_in_dangerous_goods_regulation():
    corpus_path = Path(__file__).resolve().parents[2] / "corpus" / "05_tlog_regulation_dangerous_goods.md"
    text = corpus_path.read_text(encoding="utf-8").lower()

    assert "dangerous goods" in text
    assert "awb" in text or "авиа" in text


def test_hybrid_retriever_prefers_aviation_terminal_over_office_when_aviation_query():
    chunks = [
        DocumentChunk(
            chunk_id="office-onboarding",
            content="Адаптация сотрудника в офисе компании, оформление пропуска и знакомство с командой.",
            metadata={"file": "office_onboarding.md"},
        ),
        DocumentChunk(
            chunk_id="aviation-terminal",
            content=(
                "Допуск работника грузового терминала в контролируемую зону аэропорта: "
                "пропуск, обучение aviation security, dangerous goods awareness."
            ),
            metadata={"file": "01_hr_pol_attendance.md"},
        ),
    ]

    retriever = HybridRetriever(chunks)
    results = retriever.search(
        "Какие условия допуска работника в контролируемую зону аэропорта?",
        top_k=2,
    )

    assert results[0].chunk.chunk_id == "aviation-terminal"
    assert confidence_from_results(results) >= 0.35
