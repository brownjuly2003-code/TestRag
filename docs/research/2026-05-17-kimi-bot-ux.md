## Research Summary: HR/Legal RAG Telegram-bot UX/Feedback Patterns

### 1. How Production RAG/Knowledge Bots Collect Feedback

**Current industry standard (2025-2026):**

| Platform | Feedback Pattern |
|----------|------------------|
| **Microsoft Copilot Studio** | Built-in 👍/👎 per response + optional free-text comment. Also supports custom Adaptive Cards with 5-star ratings, categories, and structured follow-up questions. |
| **Perplexity AI** | Hidden thumbs + inline «Was this helpful?» with ability to flag specific citations as incorrect. Uses RLHF loop on feedback. |
| **Intercom Fin / Ada** | Binary feedback → conditional flow: if 👎, show quick-reason buttons («Incorrect» / «Outdated» / «Not relevant») + optional text input. |
| **Enterprise RAG templates** (LangChain, LlamaIndex) | Thumbs + source-level feedback («Which source was unhelpful?») + conversation-level CSAT at session end. |

**Key insight:** Binary 👍/👎 alone is considered «primitive» because it lacks *actionable granularity*. Production systems use **multi-step feedback**: binary → categorical reason → optional free-text. This gives data to improve specific retrieval chunks, not just overall sentiment.

---

### 2. Conversational UX Patterns for Russian Corporate RAG (2025-2026)

**Channel choice for HR/legal in Russia:**
- **Telegram** dominates for external and field-staff access (pilots, cargo handlers, drivers). No corporate VPN needed.
- **Slack / Yandex Messenger / Битрикс24** work for office staff but have lower adoption in aviation operations.
- **Web widget** is best for HR self-service portal integration.

**Trending patterns in Russian enterprise bots:**
- **Thread-based conversations** (Telegram replies / Slack threads) for multi-turn legal clarifications.
- **Command menu (BotFather commands)** + **inline keyboards** hybrid — users expect both `/help` and button navigation.
- **Typing indicators** (`sendChatAction`) are mandatory for perceived performance; without them users think the bot is broken.
- **MarkdownV2/HTML formatting** — bold for conclusions, `code` for article references, expandable blockquotes for long legal excerpts (Telegram recently added native expandable blockquotes).

---

### 3. What to Add Beyond 3 Inline Buttons to Look «Production»

| Feature | Priority | Implementation Notes |
|---------|----------|----------------------|
| **Multi-step feedback flow** | **Must-have** | 👍/👎 → if 👎, show 3 reason buttons («Неточно», «Устарело», «Не по теме») → optional «Опишите проблему» free-text. Store linked to `message_id` and `retrieved_chunk_ids`. |
| **Source citations with inline links** | **Must-have** | Numbered footnotes `[1]`, `[2]` in answer text + bottom block with `<a href="doc_link">Источник: Приказ №123 от 01.01.2024</a>`. For TG use `parse_mode="HTML"`. |
| **Follow-up question buttons** | **Must-have** | 2-3 contextual suggested questions below each answer (e.g., «А какие штрафы?», «Как оформить заявку?»). Drives engagement and signals retrieval coverage. |
| **Typing indicator** | **Must-have** | `sendChatAction(chat_id, 'typing')` for 3-5s before response. Critical for LLM latency masking. |
| **HTML formatting** | **Must-have** | Use `<b>`, `<i>`, `<code>`, `<a>`, `<blockquote expandable>` for legal text structure. Never use MarkdownV2 for dynamic content — escaping is fragile. |
| **Commands: /help, /history, /clear** | **Should-have** | `/start` with role selection, `/help` with example queries, `/history` (last 5 Q&A), `/clear` to reset context. |
| **Quick-actions row** | **Should-have** | Inline buttons: «Уточнить 🔄», «Развернуть 📖», «Создать задачу 📝» (integrates with n8n → ticket system). |
| **Conversation threading** | **Should-have** | Track `thread_id` (reply chain) for follow-up context. Aviation HR questions are inherently multi-turn («А если я пилот?», «А в командировке?»). |
| **Human handover (Эскалация)** | **Should-have** | Button «🧑‍💼 Связать с HR/Legal» + capture last 5 messages for human context. |
| **Analytics/telemetry** | **Nice-to-have** | Hidden: time-to-first-token, retrieval latency, chunk relevance scores, user retention cohorts. Feed into n8n dashboard. |

---

### 4. Specific Sources & References

- **Microsoft Copilot Studio Feedback Patterns** — built-in thumbs + Adaptive Cards: https://microsoft.github.io/agent-academy/operative/11-obtain-user-feedback/
- **Wonderchat RAG Best Practices** — feedback + source attribution: https://wonderchat.io/blog/rag-genai-bots-guide
- **Telegram HTML Formatting Guide** — supported tags for bot messages: https://www.misterchatter.com/docs/telegram-html-formatting-guide-supported-tags/
- **Telegram Bot Development Guide 2025** — onboarding, commands, keyboards: https://wnexus.io/the-complete-guide-to-telegram-bot-development-in-2025/
- **Perplexity Architecture** — inline citations + continuous learning loop: referenced in Black Bear Media RAG guide
- **Enterprise AI Knowledge Bases (Egnyte Copilot vs MS Copilot vs Gemini)** — source citation UI patterns: https://intuitionlabs.ai/articles/enterprise-ai-knowledge-bases-rag-copilot

---

### 5. MVP Plan Adjustments for Aviation Cargo HR/Legal RAG

**Given your stack (Telegram + n8n + pgvector + Mistral, 200 docs, hybrid retrieval):**

**Add immediately (Must-have):**
1. **Replace static 3-button row with conditional feedback flow:**
   - Primary row: `[👍 Полезно] [👎 Неточно] [📋 Источники]`
   - On 👎: replace buttons with `[Неточный ответ] [Устарело] [Не по теме] [Другое...]`
   - On «Другое» or any 👎 reason: prompt for free-text reply, store in `feedback` table with `chunk_ids` array.
2. **Mandatory source citations:** Every answer ends with `───\n<b>Источники:</b>` block listing 2-3 top chunks with clickable doc names (HTML `<a>`). In aviation legal context, un-sourced answers are untrustworthy.
3. **Typing indicator + HTML formatting:** Use `sendChatAction` + `parse_mode="HTML"`. Structure legal answers: `<b>Краткий ответ:</b> ... <blockquote expandable><b>Подробно:</b>...</blockquote>`.

**Add next (Should-have):**
4. **Follow-up suggestions:** Generate 2 questions via lightweight Mistral call (or template-based) using retrieved chunks. Buttons appear below sources block.
5. **Command palette:** `/start` (role-aware), `/help` (5 example queries), `/history`, `/clear`.
6. **Thread memory:** Store `thread_id` in n8n; on reply-to-message, inject last 3 QA pairs into retrieval query for context-aware reformulation.
7. **Quick-actions:** «Уточнить» reruns retrieval with expanded top_k; «Перевести в задачу» posts to HR ticket system via n8n webhook.

**Defer (Nice-to-have):**
- Hidden telemetry dashboard (RAGAs metrics, latency percentiles).
- Multi-language switch (if you have non-Russian-speaking crew).
- Voice messages (not critical for legal text).

**Remove/avoid:**
- ❌ Raw MarkdownV2 (too brittle for dynamic legal citations with brackets/parentheses).
- ❌ Static 3-button feedback without conditional drill-down — this is what feels «student project».
- ❌ Answers without source attribution — in HR/legal domain this is a credibility killer.

---

### Bottom Line

Your user is right: three static buttons *are* primitive. The fix is not adding more buttons — it’s making feedback **contextual and multi-layered**, adding **verifiable source citations**, and using **Telegram-native formatting** (HTML + expandable blockquotes + inline links). For an aviation cargo company where legal precision matters, source attribution and conditional feedback are higher priority than cosmetic features like custom keyboards.
