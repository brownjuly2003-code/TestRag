# ADR 0003: Mistral для chat + embeddings (free tier)

**Status:** Accepted (Sprint 0). Re-evaluate когда rate-limit будет блокировать
прод-нагрузку или появится self-host бюджет.

**Context.** RAG-ассистент для русского + английского контента (Aviation cargo
EN-термины + RU тело документов). Нужен chat-completion для генерации
grounded-ответов + embeddings для семантического поиска. MVP-бюджет: $0.

**Decision.** Mistral API:
- chat: `mistral-small-latest` (Pixtral / Codestral fallback не нужны для plain RAG).
- embeddings: `mistral-embed` (1024-dim).
- Auth: один `MISTRAL_API_KEY` из `.env`.

Wrapper: `rag-api/app/llm.py:MistralChatClient` + `MistralEmbeddingClient`.
Sprint 6 #5: singleton `httpx.AsyncClient` (lazy init, lifespan aclose).

**Альтернативы.**

| Опция | Pro | Con |
|---|---|---|
| **Mistral API (выбрано)** | $0 free tier, RU+EN качество, JSON-mode, fast (~2-4s chat), EU-hosted | rate-limit 429 на 10 быстрых запросов (graceful degrade в `build_grounded_answer`), без enterprise SLA |
| OpenAI gpt-4o-mini + text-embedding-3-small | сильнее на edge-cases, лучше JSON-mode | $$$, US-hosted (PII concern для РФ HR-данных) |
| Anthropic Claude Haiku | better long-context (200k), citations API | $$$, EN-bias на RU |
| Self-host Llama 3.1 8B + bge-m3 | privacy + zero variable cost | нужен GPU (T4/A10), 5-10x latency vs API, оп нагрузка |
| YandexGPT + YandexEmbed | RU-native, российская юрисдикция | прайс непрозрачный, lock-in на Yandex Cloud |

**Trade-offs.**

- **Free tier rate-limit.** 10-15 req/sec → 429. `MistralChatClient.answer`
  ловит `httpx.HTTPError` → возвращает `(None, usage)` → /ask fallback'ит
  на `build_grounded_answer(...)` (bulleted-сниппеты из top-3 source chunks).
- **Dim mismatch silent failure.** Если case `mistral-embed` поменяет
  размерность (1024 → 1536) — cosine упадёт в 0 для legacy chunks. Sprint 5 #4:
  `MistralEmbeddingClient._observed_dim` pin + log.warning при mismatch.
- **Choice indexing guard.** `_extract_choice_content` (Sprint 5 #4) защищает
  от пустых `choices`, отсутствующего `message`, не-str `content` — раньше
  падало 500. JSON-decode тоже в try/except.
- **Russian inflection.** `mistral-embed` достаточно ловит парафразы
  («испытательный срок» / «срок испытания»). Eval подтверждает: golden Q
  «продление испытательного срока» → top-1 `01_hr_probation_procedure.md`
  при vector_score 0.85+.

**Consequences.**

- ✅ MVP-стоимость $0 на dev, ~$10-30/мес на demo трафике.
- ✅ HTTP pooling Sprint 6 #5 убрал TLS handshake — eval CI 71s → 29s.
- ⚠️ Vendor lock. Mitigation: `MistralChatClient` / `MistralEmbeddingClient`
  абстракции — swap на другого провайдера ≤ 50 строк (config + payload diff).
- ⚠️ EU-hosted, но не РФ. Если HR-данные требуют РФ-резидентности —
  миграция на YandexGPT / GigaChat. Не блокер для public demo corpus.
