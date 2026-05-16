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
- `opus_result_followup_risk_burndown.md` - risk burn-down.

Codex is continuing implementation and may edit `rag-api/**`, docs, compose, `.env`, manifests, and `n8n/**`. Codex also owns the live Telegram/n8n routing fix.

Status update 2026-05-16: Codex fixed the live greeting regression. The bot now replies to `привет`/`/start` through a direct-reply route without calling `/ask`, and Telegram send nodes no longer append the n8n attribution line. The follow-up reports below are kept as pre-fix triage/spec artifacts.

## Hard Rules

- Do not read or print `.env`, tokens, keys, cookies, credentials, or Telegram webhook tokens.
- Do not modify `corpus/`, `rag-api/`, `sql/`, `n8n/`, `.env`, `.env.example`, `docker-compose.yml`, `mvp-plan.md`, `README.md`, or `docs/`.
- Do not run Docker, database, Telegram, webhook, or external API commands.
- Write only new report files named `opus_result_followup_<topic>.md`.
- If a task needs a secret, live Telegram account, running container, or DB mutation, mark it blocked and move on.

## Next Tasks

- [x] Static Telegram workflow triage for silent greeting. Verify: `opus_result_followup_greeting_route_triage.md` written; superseded by the Codex direct-reply fix but useful as incident triage history.
- [x] Greeting and small-talk response contract. Verify: `opus_result_followup_greeting_contract.md` written; core greeting/empty/thanks behavior implemented in n8n.
- [x] Silent-bot failure-mode checklist. Verify: `opus_result_followup_silent_bot_checklist.md` written.
- [x] Regression test spec for Codex. Verify: `opus_result_followup_telegram_regression_spec.md` written; implemented critical workflow regression coverage in `rag-api/tests/test_n8n_workflow.py`.
- [x] Demo recovery plan. Verify: `opus_result_followup_demo_recovery.md` written.

## Current Codex Verification

- `python -m pytest -p no:schemathesis` -> 25 passed.
- `docker compose config --quiet` -> ok.
- `git diff --check` -> ok.
- `/health` -> `status=ok`, `chunk_count=135`.
- Live `/ask` for the st. 70 probation question says that probation cannot be extended and cites updated sources.

## Next Tasks

- No pending Opus offline tasks in this handoff.

## Non-Goals

- Do not implement fixes.
- Do not change project files other than `opus_result_followup_*.md`.
- Do not validate live Telegram.
- Do not re-run ingestion or alter database contents.
