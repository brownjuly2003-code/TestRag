# ADR 0002: BM25 in-memory + pgvector hybrid retriever

**Status:** Accepted (Sprint 0). Re-evaluate если корпус превысит ~5000 chunks.

**Context.** ~200 markdown файлов (~189 чанков по 500 токенов). Нужно гибрид
keyword + semantic поиск: HR/legal термины часто требуют точного совпадения
(«статья 70», AWB, GHA), но семантический ретривер ловит парафразы.

**Decision.** BM25 реализован в Python (`rag-api/app/rag.py:HybridRetriever`)
поверх in-memory списка `DocumentChunk`. Vector search — pgvector cosine
из postgres (chunks ingest'ятся на startup с embeddings от Mistral).
Финальный score = `0.65*BM25 + 0.35*vector × coverage^2 × (1+section_boost)`.

**Альтернативы.**

| Опция | Pro | Con |
|---|---|---|
| **In-memory BM25 + pgvector (выбрано)** | Zero infra: numpy не нужен, чистый Python. ~200ms на 189 чанках. Веса env-параметризованы (`HYBRID_*`). Reproducible — eval/baseline.json коммитится. | O(N) на каждый запрос. Не масштабируется за ~5000 чанков. Index hot-reload требует rag-api restart. |
| Elasticsearch / OpenSearch | масштабируется, hot-update, готовый BM25+vector | +1 stateful сервис, операционная сложность, дороже на dev |
| Postgres `tsvector` + `pgvector` | один storage backend, ACID | Russian morphology в `tsvector` слабая (нет лемматизатора без extra), нужны кастомные суффиксные правила |
| Pinecone / Weaviate (managed) | zero ops, vector + filter native | external dependency, $/мес, latency через WAN, lock-in |

**Trade-offs.**

- **Latency budget.** Sprint 4-5 финальный MRR=0.76 / Hit@1=0.67 / Hit@5=0.89
  на 189 чанках при ~30-200ms retrieval. Mistral chat dominates latency
  (~2-4s), retrieval — не bottleneck.
- **Russian morphology.** `tokenize()` + `_normalize_token()` стрипают
  ~30 русских суффиксов («путевого»→«путево»). Хватает для домена (HR/legal/
  aviation cargo), но не lemma-quality. Sprint 7+ option: pymorphy3 на ingest.
- **Section keyword rerank** (`_section_boost`) — Sprint 5: chunk с query-term
  в `section` metadata получает +10% per overlap, capped +30%. Закрыл часть
  проблем top-1 после aviation pass (Hit@1 0.44 → 0.67).
- **Empty/stop-word query** — Sprint 6 #4: пустые токены → vector-only
  fallback на query_embedding (см. `_vector_only_search`).

**Consequences.**

- ✅ Eval reproducible: `scripts/eval_retrieval.py` + `eval/baseline.json` +
  `scripts/test_eval_regression.py` (floor MRR≥0.60, Hit@1≥0.50, Hit@5≥0.75).
- ✅ Веса tunable через env без code-change.
- ⚠️ Корпус > 5000 чанков — пора Elasticsearch / managed vector store.
- ⚠️ BM25 пересчитывается на каждый /ask. Кешировать `document_frequencies`
  на runtime — уже сделано (`HybridRetriever.__init__`). Per-query cost — O(N×|tokens|).
