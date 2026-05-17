"""Sprint 6 #7: Multi-turn A/B ablation harness.

Прогоняет multi-turn golden set дважды:
  • prev_qa_count=0 (baseline, current behavior)
  • prev_qa_count=2 (Prev-N-QA augmentation)

И печатает delta по Hit@1, Hit@5, MRR.

Каждый кейс — последовательность turns: первые turn'ы прогреваются, чтобы
populate request_logs у telegram_user_id; последний turn — оцениваемый.

Запуск (требует docker compose up rag-api + postgres):
    python scripts/eval_multiturn.py
    python scripts/eval_multiturn.py --output .tmp/eval_multiturn.json
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import requests


API = "http://localhost:8000"
# Distinct user id для каждого case (изоляция history)
USER_PREFIX = "eval-mt-"


# Каждый case = setup turns (прогрев history) + evaluated turn (последний).
GOLDEN_CASES: list[dict[str, Any]] = [
    {
        "name": "controlled_zone_followup",
        "setup": [
            "Что такое controlled zone?",
        ],
        "evaluated": {
            "q": "А кто туда имеет доступ?",
            "expected_files": ["01_hr_pol_safety", "06_comp", "07_faq_expedition"],
        },
    },
    {
        "name": "dangerous_goods_doc_lifespan",
        "setup": [
            "Какие документы нужны для отправки dangerous goods авиатранспортом?",
        ],
        "evaluated": {
            "q": "А срок их действия?",
            "expected_files": ["06_comp", "05_tlog", "07_faq_expedition"],
        },
    },
    {
        "name": "awb_mawb_breakdown",
        "setup": [
            "Что такое AWB и MAWB?",
        ],
        "evaluated": {
            "q": "А HAWB?",
            "expected_files": ["05_tlog", "07_faq_expedition"],
        },
    },
    {
        "name": "probation_extension_check",
        "setup": [
            "Какой испытательный срок по ТК РФ?",
        ],
        "evaluated": {
            "q": "Можно ли его продлить?",
            "expected_files": ["01_hr_probation", "07_faq_probation", "external_tk_rf"],
        },
    },
    {
        "name": "claim_procedure_followup",
        "setup": [
            "Как составить претензию контрагенту?",
        ],
        "evaluated": {
            "q": "В какой срок она должна быть рассмотрена?",
            "expected_files": ["04_legal_cla", "07_faq_claims_procedure"],
        },
    },
]


def ask(api: str, question: str, user_id: str, *, prev_qa_count: int = 0, top_k: int = 5) -> dict[str, Any]:
    r = requests.post(
        f"{api}/ask",
        json={
            "question": question,
            "telegram_user_id": user_id,
            "top_k": top_k,
            "prev_qa_count": prev_qa_count,
        },
        timeout=120,
    )
    r.raise_for_status()
    return r.json()


def score(response: dict[str, Any], expected_files: list[str]) -> dict[str, Any]:
    sources = response.get("sources") or []
    files = [s.get("file") or "" for s in sources]
    hit1 = 0
    hit5 = 0
    rank = None
    for idx, fname in enumerate(files):
        if any(exp in fname for exp in expected_files):
            hit5 = 1
            if idx == 0:
                hit1 = 1
            rank = idx + 1
            break
    return {
        "hit@1": hit1,
        "hit@5": hit5,
        "rank": rank,
        "top_files": files[:5],
        "confidence": response.get("confidence"),
    }


def run_case(api: str, case: dict[str, Any], prev_qa_count: int) -> dict[str, Any]:
    user_id = f"{USER_PREFIX}{case['name']}-pq{prev_qa_count}"
    # Прогрев: setup turns (история наполняется)
    for q in case["setup"]:
        ask(api, q, user_id, prev_qa_count=0)
        time.sleep(0.1)  # рейтлимит Mistral free tier
    # Оцениваемый turn
    started = time.perf_counter()
    resp = ask(api, case["evaluated"]["q"], user_id, prev_qa_count=prev_qa_count)
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    metrics = score(resp, case["evaluated"]["expected_files"])
    return {
        "case": case["name"],
        "evaluated_q": case["evaluated"]["q"],
        "expected_files": case["evaluated"]["expected_files"],
        "prev_qa_count": prev_qa_count,
        "latency_ms": elapsed_ms,
        **metrics,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {}
    rrs = [1.0 / r["rank"] for r in rows if r.get("rank")]
    return {
        "n": len(rows),
        "hit@1": round(sum(r["hit@1"] for r in rows) / len(rows), 4),
        "hit@5": round(sum(r["hit@5"] for r in rows) / len(rows), 4),
        "mrr": round(sum(rrs) / len(rows), 4) if rrs else 0.0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--api", default=API)
    args = parser.parse_args()
    api = args.api.rstrip("/")

    print(f"Multi-turn ablation on {len(GOLDEN_CASES)} cases · A=prev_qa_count=0 · B=prev_qa_count=2\n")
    arm_a: list[dict[str, Any]] = []
    arm_b: list[dict[str, Any]] = []
    for case in GOLDEN_CASES:
        a = run_case(api, case, prev_qa_count=0)
        b = run_case(api, case, prev_qa_count=2)
        delta = "→" if a["hit@1"] == b["hit@1"] else ("↑" if b["hit@1"] > a["hit@1"] else "↓")
        print(f"  [{case['name']}] A:hit1={a['hit@1']} rank={a['rank']}  B:hit1={b['hit@1']} rank={b['rank']}  {delta}")
        arm_a.append(a)
        arm_b.append(b)

    sum_a = summarize(arm_a)
    sum_b = summarize(arm_b)
    print("\n=== A (prev_qa_count=0) ===")
    for k, v in sum_a.items():
        print(f"  {k}: {v}")
    print("\n=== B (prev_qa_count=2) ===")
    for k, v in sum_b.items():
        print(f"  {k}: {v}")
    print("\n=== DELTA (B - A) ===")
    for k in ["hit@1", "hit@5", "mrr"]:
        d = sum_b[k] - sum_a[k]
        sign = "+" if d > 0 else ""
        print(f"  Δ{k}: {sign}{round(d, 4)}")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(
                {"a_baseline": {"summary": sum_a, "rows": arm_a},
                 "b_prev_qa_2": {"summary": sum_b, "rows": arm_b}},
                ensure_ascii=False, indent=2,
            ),
            encoding="utf-8",
        )
        print(f"\nSaved to {args.output}")

    # Не падаем — это ablation, информация, не gate
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
