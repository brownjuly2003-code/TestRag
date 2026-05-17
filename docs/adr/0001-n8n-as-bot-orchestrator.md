# ADR 0001: n8n как orchestrator Telegram-бота

**Status:** Accepted (Sprint 1, 2026-05-16). Re-evaluate в Sprint 6+ (issue #1 из mvp-plan).

**Context.** TestRag MVP — Telegram-бот для HR/legal/logistics. Нужно склеить:
TG Webhook → whitelist user_id → typing indicator → POST `rag-api:/ask` →
MD→HTML конверсия + 4 inline-кнопки → split-output → callback handlers
(👍/👎, 📎 follow-up, 🧑‍💼 human). Около 28 узлов flow.

**Decision.** Self-hosted n8n (docker-compose, pin 1.103.2) с одним workflow
`hr-legal-rag-workflow.json`. rag-api как Python FastAPI с retrieval+LLM
endpoints — без знаний о Telegram. Граница: n8n знает Telegram, rag-api
знает retrieval.

**Альтернативы.**

| Опция | Pro | Con |
|---|---|---|
| **n8n self-hosted (выбрано)** | визуальный flow, готовые TG/HTTP nodes, log replay, hot-edit без redeploy | docker-зависимость, secret_token in-memory (issue #2 в known-issues), JS-куски в нодах сложно тестировать unit-level |
| Полный FastAPI бот (python-telegram-bot/aiogram) | один runtime, нет n8n как BlackBox, лёгко тестировать | переписать всю TG-логику с нуля, потеря visual flow editor для не-разработчика |
| Lambda + EventBridge | serverless, dev-cost ноль | cold start TG webhook (3-5s), AWS vendor lock-in для MVP |

**Trade-offs.**

- **Coupling.** Whitelist check / command routing / `/help` copy сейчас в JS-нодах n8n. Sprint 6 #1 backlog: extract в rag-api endpoints `/auth/check` + `/commands`, после — `N8N_BLOCK_ENV_ACCESS_IN_NODE=true` (mvp-plan.md L130-134).
- **Testability.** unit-тесты на workflow логику читают `workflow.json` напрямую и парсят `parameters.jsCode` — 28 узлов покрыты 18 тестами (search для `rag-api/tests/test_n8n_workflow*.py`).
- **E2E.** TelegramTrigger v1.3 random secret_token in-memory ⇒ синтетический webhook POST → 403. Workaround — live TG smoke через @AIagentJu_bot user account (см. `scripts/smoke_tg_e2e.py`).

**Consequences.**

- ✅ MVP shipped за 5 sprint'ов (28 nodes vs ~600 строк python).
- ✅ Hot-edit формулировок копи через n8n UI без redeploy.
- ⚠️ Business logic размазана: rag-api retrieval/LLM + n8n routing/UI. Sprint 6 #1 это сворачивает.
- ⚠️ Один workflow JSON — merge-конфликты при паре правок одновременно. Mitigation: `git diff --word-diff` + import:workflow по projectId.
