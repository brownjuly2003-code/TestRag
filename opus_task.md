# Opus Parallel Tasks

## Context

Previous Opus pass produced:

- `opus_result_corpus.md` - 30-file shortlist with category rationale and refusal reserves.
- `opus_result_demo_questions.md` - 12 demo questions with intent, expected behavior, and pass/fail.
- `opus_result_docs_consistency.md` - 12 documentation findings.
- `opus_result_checklist.md` - 17-step 10-minute pre-demo checklist.
- `opus_result_risks.md` - 12 ranked demo risks with mitigations and owners.
- `opus_result_next_manifest_delta.md` - manifest additions/removals and 38/30/42 size options.
- `opus_result_next_demo_script.md` - 6-question demo flow with fallbacks.
- `opus_result_next_presenter_checklist.md` - presenter-safe PowerShell checklist.
- `opus_result_next_disclaimer.md` - synthetic-corpus disclaimers for slides, Telegram, and README.
- `opus_result_next_docs_delta.md` - remaining documentation deltas after Codex changes.
- `opus_result_followup_manifest_decision.md` - preferred manifest decision.
- `opus_result_followup_answer_matrix.md` - offline answer-quality matrix.
- `opus_result_followup_telegram_copy.md` - Telegram-facing copy draft.
- `opus_result_followup_docs_patch_plan.md` - docs patch plan.

Codex is continuing implementation and may edit `rag-api/**`, docs, compose, `.env`, manifests, and `n8n/**`. Codex also owns the live Telegram/n8n routing fix. Do not edit those files and do not run live checks.

## Hard Rules

- Do not read or print `.env`, tokens, keys, cookies, credentials, or Telegram webhook tokens.
- Do not modify `corpus/`, `rag-api/`, `sql/`, `n8n/`, `.env`, `.env.example`, `docker-compose.yml`, `mvp-plan.md`, `README.md`, or `docs/`.
- Do not run Docker, database, Telegram, webhook, or external API commands.
- Write only new report files named `opus_result_followup_<topic>.md`.
- If a task needs a secret, live Telegram account, running container, or DB mutation, mark it blocked and move on.

## Next Tasks

- [x] Consolidate manifest recommendation. Verify: write `opus_result_followup_manifest_decision.md` with one preferred manifest option, exact add/remove list, demo-question impact, and why alternatives were rejected.
- [x] Build an offline answer-quality matrix. Verify: write `opus_result_followup_answer_matrix.md` mapping each selected demo question to expected source files, must-have answer points, refusal/pass criteria, and fallback wording.
- [x] Draft Telegram-facing copy only. Verify: write `opus_result_followup_telegram_copy.md` with concise Russian text for greeting, refusal, low-confidence answer, feedback confirmation, whitelist denial, and synthetic-corpus disclaimer.
- [x] Prepare docs patch plan without editing docs. Verify: write `opus_result_followup_docs_patch_plan.md` with target file/section, proposed wording, and priority for each remaining documentation gap.
- [ ] Update demo risk burn-down. Verify: write `opus_result_followup_risk_burndown.md` with top remaining risks after the current Codex fixes, owner, mitigation, and a 10-minute go/no-go signal.

## Non-Goals

- Do not implement fixes.
- Do not change project files other than `opus_result_followup_*.md`.
- Do not validate live Telegram.
- Do not re-run ingestion or alter database contents.
