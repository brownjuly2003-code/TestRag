# Architecture Decision Records

Sprint 6 #2: фиксируем 3 ключевых архитектурных выбора TestRag MVP, чтобы
не пересматривать одни и те же trade-offs из сессии в сессию.

| ADR | Title | Status |
|---|---|---|
| [0001](0001-n8n-as-bot-orchestrator.md) | n8n как orchestrator Telegram-бота | Accepted, re-evaluate в Sprint 6+ |
| [0002](0002-in-memory-bm25-hybrid-retriever.md) | BM25 in-memory + pgvector hybrid retriever | Accepted, threshold ~5000 chunks |
| [0003](0003-mistral-as-llm-and-embeddings.md) | Mistral для chat + embeddings (free tier) | Accepted, re-evaluate при rate-limit на проде |

## Когда писать новый ADR

- Меняем provider (LLM, embeddings, vector store, bot platform).
- Меняем границы между компонентами (rag-api ⇄ n8n).
- Меняем core retrieval-алгоритм (BM25 → splade, hybrid → late interaction).
- Внедряем feature flag / kill switch с долгим хвостом.

NB: tactical-фиксы (новый chunk slugger, новый /ask поле) — не нуждаются в ADR.
ADR пишется когда **другой инженер через год** должен понять *почему*, а не *что*.
