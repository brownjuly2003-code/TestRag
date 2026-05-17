"""Sprint 6 #7: Prev-N-QA retrieval augmentation.

При prev_qa_count > 0 берём последние N (вопрос, ответ) пользователя
из request_logs и подмешиваем в retrieval-запрос. LLM prompt НЕ
augmented — это снижает риск дрейфа в ответе при off-topic-контексте.

Гипотеза: для follow-up-вопросов вроде «А ещё?» / «Уточни», у которых
ключевые сущности были в предыдущем turn'е, augmentation поднимает
Hit@1. На независимых вопросах — нейтрально или slight noise.
A/B harness: scripts/eval_multiturn.py.
"""
from __future__ import annotations

from typing import Any


def augment_retrieval_query(
    current_question: str,
    prev_qas: list[dict[str, Any]],
    *,
    max_prev: int = 3,
    include_answers: bool = False,
) -> str:
    """Конкатенирует current_question с последними prev_qas[:max_prev].

    Параметры:
        current_question: текущий вопрос (всегда последним, чтобы embedding
            акцентировался на нём).
        prev_qas: список dict с ключами 'question' и (опц.) 'answer'.
            Ожидается order desc по created_at (как `recent_requests`).
        max_prev: лимит prev turns (default 3 = баланс контекста vs шума).
        include_answers: включать ли answer-текст. Default False — answers
            обычно длинные и могут размывать query-вектор.

    Возвращает augmented string или current_question если prev_qas пуст
    или max_prev=0.
    """
    if not prev_qas or max_prev <= 0 or not current_question.strip():
        return current_question

    selected = prev_qas[:max_prev]
    parts: list[str] = []
    for qa in selected:
        q = (qa.get("question") or "").strip()
        if q:
            parts.append(q)
        if include_answers:
            a = (qa.get("answer") or "").strip()
            if a:
                parts.append(a)
    parts.append(current_question.strip())
    return " | ".join(parts)


def filter_relevant_prev_qas(
    prev_qas: list[dict[str, Any]],
    *,
    skip_refused: bool = True,
    min_confidence: float = 0.0,
) -> list[dict[str, Any]]:
    """Отфильтровывает refusal'ы и low-confidence turns из истории —
    они не несут полезных query-сигналов, только шум."""
    out: list[dict[str, Any]] = []
    for qa in prev_qas:
        if skip_refused and qa.get("refused") is True:
            continue
        conf = qa.get("confidence")
        if conf is not None and float(conf) < min_confidence:
            continue
        out.append(qa)
    return out
