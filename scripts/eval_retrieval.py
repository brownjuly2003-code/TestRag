"""Eval pipeline (critique #8): прогоняет golden questions через /ask, считает
Hit@1, Hit@5, MRR, refusal_rate, avg_latency_ms, avg_confidence.

Использование:
    python scripts/eval_retrieval.py
    python scripts/eval_retrieval.py --output .tmp/eval_baseline.json

Golden set встроен в скрипт. Расширяй GOLDEN_QUESTIONS перед Sprint 4
retrieval polish, чтобы baseline сравнить с после-fix цифрами.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any

import requests

API = "http://localhost:8000"

# Каждый item: question + expected_file (substring matched), optional expected_section,
# optional expected_refused (если True, ожидаем status='unanswerable').
GOLDEN_QUESTIONS: list[dict[str, Any]] = [
    {
        "q": "Что такое controlled zone?",
        "expected_file": "01_hr_pol_safety",
        "expected_refused": False,
    },
    {
        "q": "Какие документы нужны для отправки dangerous goods авиатранспортом?",
        "expected_file": "06_comp",
        "expected_refused": False,
    },
    {
        "q": "Какие основания для досрочного расторжения трудового договора?",
        "expected_file": "07_faq_dismissal",
        "expected_refused": False,
    },
    {
        "q": "Что такое AWB и MAWB?",
        "expected_file": "05_tlog",
        "expected_refused": False,
    },
    {
        "q": "Какой испытательный срок по ТК РФ?",
        "expected_file": "01_hr_probation",
        "expected_refused": False,
    },
    {
        "q": "Какой максимальный размер ULD для авиаперевозки?",
        "expected_file": "05_tlog",
        "expected_refused": False,
    },
    {
        "q": "Как составить претензию контрагенту?",
        "expected_file": "04_legal_cla",
        "expected_refused": False,
    },
    {
        "q": "Какие правила для cutoff time в авиагрузовых перевозках?",
        "expected_file": "05_tlog",
        "expected_refused": False,
    },
    # Off-corpus refusal: тематика которой нет в базе.
    {
        "q": "Какие документы нужны для отправки лития морем?",
        "expected_file": None,
        "expected_refused": True,
    },
    {
        "q": "Что такое GHA?",
        "expected_file": "05_tlog",
        "expected_refused": False,
    },
]


def ask(api: str, question: str, top_k: int = 5) -> dict[str, Any]:
    r = requests.post(
        f"{api}/ask",
        json={"question": question, "telegram_user_id": "eval-bot", "top_k": top_k},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()


def evaluate_one(api: str, item: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    response = ask(api, item["q"])
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    expected_file = item.get("expected_file")
    sources = response.get("sources") or []
    files = [s.get("file") or "" for s in sources]

    hit_at_1 = 0
    hit_at_5 = 0
    rank = None
    if expected_file:
        for idx, fname in enumerate(files):
            if expected_file in fname:
                hit_at_5 = 1
                if idx == 0:
                    hit_at_1 = 1
                rank = idx + 1
                break

    refused = response.get("refused", False)
    refusal_correct = refused == item.get("expected_refused", False)

    return {
        "q": item["q"],
        "expected_file": expected_file,
        "expected_refused": item.get("expected_refused", False),
        "top_files": files[:5],
        "status": response.get("status"),
        "refused": refused,
        "refusal_correct": refusal_correct,
        "confidence": response.get("confidence"),
        "latency_ms": response.get("latency_ms") or elapsed_ms,
        "hit@1": hit_at_1,
        "hit@5": hit_at_5,
        "rank": rank,
        "request_log_id": response.get("request_log_id"),
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    answerable = [r for r in rows if not r["expected_refused"]]
    refusal_cases = [r for r in rows if r["expected_refused"]]
    rrs = [1.0 / r["rank"] for r in answerable if r.get("rank")]
    return {
        "total": len(rows),
        "answerable_total": len(answerable),
        "refusal_total": len(refusal_cases),
        "hit@1": round(sum(r["hit@1"] for r in answerable) / len(answerable), 4) if answerable else 0,
        "hit@5": round(sum(r["hit@5"] for r in answerable) / len(answerable), 4) if answerable else 0,
        "mrr": round(sum(rrs) / len(answerable), 4) if answerable else 0,
        "refusal_accuracy": round(
            sum(1 for r in rows if r["refusal_correct"]) / len(rows), 4
        ) if rows else 0,
        "avg_latency_ms": int(statistics.mean(r["latency_ms"] for r in rows)) if rows else 0,
        "avg_confidence": round(
            statistics.mean(r["confidence"] for r in rows if r["confidence"] is not None), 4
        ) if rows else 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=None, help="Сохранить JSON в файл.")
    parser.add_argument("--api", default=API, help="RAG API URL (default http://localhost:8000).")
    args = parser.parse_args()

    api = args.api.rstrip("/")
    print(f"Eval against {api} on {len(GOLDEN_QUESTIONS)} golden questions...\n")
    rows: list[dict[str, Any]] = []
    for item in GOLDEN_QUESTIONS:
        row = evaluate_one(api, item)
        marker = "✓" if row["hit@1"] else ("○" if row["hit@5"] else "✗")
        refusal_marker = "✓" if row["refusal_correct"] else "✗"
        print(
            f"  {marker} '{row['q'][:60]}' hit@1={row['hit@1']} hit@5={row['hit@5']} "
            f"rank={row['rank']} status={row['status']} refusal{refusal_marker}"
        )
        rows.append(row)

    summary = summarize(rows)
    print("\n=== SUMMARY ===")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"\nSaved to {args.output}")

    # Exit code: 1 если MRR < 0.4 или refusal_accuracy < 0.9 (gate для CI).
    if summary["mrr"] < 0.4 or summary["refusal_accuracy"] < 0.9:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
