from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
import math
import os
import re
from typing import Any


TOKEN_RE = re.compile(r"[A-Za-zА-Яа-яЁё0-9]+", re.UNICODE)
STOP_WORDS = {
    "а",
    "без",
    "в",
    "во",
    "для",
    "до",
    "если",
    "и",
    "или",
    "как",
    "какая",
    "какие",
    "какой",
    "какую",
    "когда",
    "ли",
    "может",
    "можно",
    "на",
    "не",
    "нужен",
    "нужна",
    "нужно",
    "нужны",
    "о",
    "об",
    "от",
    "по",
    "при",
    "про",
    "с",
    "со",
    "что",
}
RUSSIAN_SUFFIXES = (
    "иями",
    "ями",
    "ого",
    "ему",
    "ому",
    "ыми",
    "ими",
    "ая",
    "ее",
    "ие",
    "ий",
    "ия",
    "ой",
    "ом",
    "ым",
    "ых",
    "ые",
    "ам",
    "ах",
    "ев",
    "ей",
    "ем",
    "ие",
    "ию",
    "ия",
    "ов",
    "ям",
    "ях",
    "а",
    "е",
    "и",
    "о",
    "у",
    "ы",
    "я",
)


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    embedding: list[float] | None = None


@dataclass(frozen=True)
class SearchResult:
    chunk: DocumentChunk
    bm25_score: float
    vector_score: float
    final_score: float
    # Sprint 6 #3: explainability breakdown (codex-audit#6.3).
    # Defaults сохраняют backwards-compat для построителей SearchResult вне HybridRetriever.
    normalized_bm25: float = 0.0
    coverage: float = 0.0
    section_boost: float = 0.0


@dataclass(frozen=True)
class AnswerPolicy:
    min_confidence: float = 0.35
    min_sources: int = 1

    def can_answer(self, confidence: float, source_count: int) -> bool:
        return confidence >= self.min_confidence and source_count >= self.min_sources


def tokenize(text: str) -> list[str]:
    tokens = []
    for raw_token in TOKEN_RE.findall(text):
        token = raw_token.lower().replace("ё", "е")
        if len(token) <= 1 or token in STOP_WORDS:
            continue
        normalized = _normalize_token(token)
        if len(normalized) > 1 and normalized not in STOP_WORDS:
            tokens.append(normalized)
    return tokens


def _normalize_token(token: str) -> str:
    if token.isascii() or token.isdigit() or len(token) <= 4:
        return token
    for suffix in RUSSIAN_SUFFIXES:
        if token.endswith(suffix) and len(token) - len(suffix) >= 4:
            return token[: -len(suffix)]
    return token


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


class HybridRetriever:
    # Sprint 5 #5: hybrid retrieval веса параметризуются через env.
    # Defaults — текущий Sprint 5 baseline (MRR=0.76).
    # Меняй только осознанно: каждое изменение → перепрогон scripts/eval_retrieval.py.
    BM25_WEIGHT = float(os.getenv("HYBRID_BM25_WEIGHT", "0.65"))
    VECTOR_WEIGHT = float(os.getenv("HYBRID_VECTOR_WEIGHT", "0.35"))
    COVERAGE_EXP = float(os.getenv("HYBRID_COVERAGE_EXP", "2.0"))
    SECTION_BOOST_PER_TERM = float(os.getenv("HYBRID_SECTION_BOOST_PER_TERM", "0.10"))
    SECTION_BOOST_MAX = float(os.getenv("HYBRID_SECTION_BOOST_MAX", "0.30"))

    def __init__(self, chunks: list[DocumentChunk], k1: float = 1.5, b: float = 0.75) -> None:
        self.chunks = chunks
        self.k1 = k1
        self.b = b
        self.doc_tokens = [tokenize(chunk.content) for chunk in chunks]
        self.term_frequencies = [Counter(tokens) for tokens in self.doc_tokens]
        self.doc_lengths = [len(tokens) for tokens in self.doc_tokens]
        self.avg_doc_length = sum(self.doc_lengths) / len(self.doc_lengths) if self.doc_lengths else 0.0
        self.document_frequencies = self._build_document_frequencies()

    def search(
        self,
        query: str,
        top_k: int = 5,
        query_embedding: list[float] | None = None,
    ) -> list[SearchResult]:
        if top_k <= 0:
            return []
        query_tokens = tokenize(query)
        if not query_tokens:
            return self._vector_only_search(query_embedding, top_k)

        query_terms = set(query_tokens)
        bm25_scores = [self._bm25_score(query_tokens, index) for index in range(len(self.chunks))]
        max_bm25 = max(bm25_scores) if bm25_scores else 0.0
        has_vector = query_embedding is not None and any(chunk.embedding for chunk in self.chunks)

        results: list[SearchResult] = []
        for index, chunk in enumerate(self.chunks):
            bm25_score = bm25_scores[index]
            normalized_bm25 = bm25_score / max_bm25 if max_bm25 > 0 else 0.0
            vector_score = 0.0
            if has_vector and chunk.embedding:
                vector_score = (cosine_similarity(query_embedding or [], chunk.embedding) + 1) / 2
            coverage = len(query_terms.intersection(self.term_frequencies[index])) / len(query_terms)
            base_score = (
                self.BM25_WEIGHT * normalized_bm25 + self.VECTOR_WEIGHT * vector_score
                if has_vector
                else normalized_bm25
            )
            section_boost = self._section_boost(query_terms, chunk)
            final_score = base_score * (coverage ** self.COVERAGE_EXP) * (1.0 + section_boost)
            results.append(
                SearchResult(
                    chunk=chunk,
                    bm25_score=bm25_score,
                    vector_score=vector_score,
                    final_score=final_score,
                    normalized_bm25=normalized_bm25,
                    coverage=coverage,
                    section_boost=section_boost,
                )
            )

        return sorted(results, key=lambda item: item.final_score, reverse=True)[:top_k]

    def _vector_only_search(
        self, query_embedding: list[float] | None, top_k: int
    ) -> list[SearchResult]:
        # Sprint 6 #4: когда BM25 tokens=[] (стоп-слова, кириллица<2, эмодзи),
        # отдаём семантический fallback вместо пустого ответа.
        if query_embedding is None:
            return []
        if not any(chunk.embedding for chunk in self.chunks):
            return []
        results: list[SearchResult] = []
        for chunk in self.chunks:
            if not chunk.embedding:
                continue
            vector_score = (cosine_similarity(query_embedding, chunk.embedding) + 1) / 2
            results.append(
                SearchResult(
                    chunk=chunk,
                    bm25_score=0.0,
                    vector_score=vector_score,
                    final_score=vector_score,
                )
            )
        return sorted(results, key=lambda item: item.final_score, reverse=True)[:top_k]

    @classmethod
    def _section_boost(cls, query_terms: set[str], chunk: DocumentChunk) -> float:
        section = (chunk.metadata.get("section") or "") if chunk.metadata else ""
        if not section or not query_terms:
            return 0.0
        section_tokens = set(tokenize(section))
        if not section_tokens:
            return 0.0
        overlap = len(query_terms & section_tokens)
        if not overlap:
            return 0.0
        # Каждое совпадение query-term с section-token даёт +N% к score, потолок +M%.
        return min(cls.SECTION_BOOST_MAX, overlap * cls.SECTION_BOOST_PER_TERM)

    def _build_document_frequencies(self) -> Counter[str]:
        frequencies: Counter[str] = Counter()
        for tokens in self.doc_tokens:
            frequencies.update(set(tokens))
        return frequencies

    def _bm25_score(self, query_tokens: list[str], doc_index: int) -> float:
        if not self.chunks or self.avg_doc_length == 0:
            return 0.0

        score = 0.0
        term_frequency = self.term_frequencies[doc_index]
        doc_length = self.doc_lengths[doc_index]
        total_documents = len(self.chunks)

        for token in query_tokens:
            frequency = term_frequency.get(token, 0)
            if frequency == 0:
                continue
            doc_frequency = self.document_frequencies[token]
            idf = math.log(1 + (total_documents - doc_frequency + 0.5) / (doc_frequency + 0.5))
            denominator = frequency + self.k1 * (1 - self.b + self.b * doc_length / self.avg_doc_length)
            score += idf * (frequency * (self.k1 + 1)) / denominator

        return score


def confidence_from_results(results: list[SearchResult]) -> float:
    if not results:
        return 0.0
    strong_sources = sum(1 for result in results if result.final_score >= 0.35)
    source_bonus = min(0.1, strong_sources * 0.025)
    return min(1.0, results[0].final_score + source_bonus)


def build_grounded_answer(question: str, results: list[SearchResult]) -> str:
    relevant = [result for result in results if result.final_score > 0]
    if not relevant:
        return "Не нашел достаточных источников для ответа. Уточните вопрос или добавьте документы в базу знаний."

    bullets = []
    for result in relevant[:3]:
        snippet = result.chunk.content.strip().replace("\n", " ")
        if len(snippet) > 260:
            snippet = snippet[:257].rstrip() + "..."
        bullets.append(f"- {snippet}")

    return "По найденным источникам:\n" + "\n".join(bullets)
