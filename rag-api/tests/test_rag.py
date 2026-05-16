from app.rag import AnswerPolicy, DocumentChunk, HybridRetriever, confidence_from_results


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
