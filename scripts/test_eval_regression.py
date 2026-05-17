"""Eval regression gate (Sprint 5 #2).

Запускать через pytest: ``pytest scripts/test_eval_regression.py``.

Прогоняет ``scripts/eval_retrieval.py``  и проверяет, что метрики не упали ниже
floor'ов, согласованных в Sprint 5. Используется как CI gate перед merge: если
кто-то поломал retrieval — pytest упадёт с конкретным diff.

Skip-условие: если ``http://localhost:8000/health`` не отвечает 200 — тест
помечается skipped (CI запустит eval только когда API поднят).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

API = os.getenv("RAG_API_URL", "http://localhost:8000").rstrip("/")

# Floor'ы Sprint 5 (post-content-enrichment baseline: MRR=0.76, Hit@1=0.67,
# Hit@5=0.89, refusal=1.0, avg_confidence=0.85). Floor — это «не ниже этого»,
# не текущее значение. Cushion ~10pp от baseline защищает от noise/Mistral 429.
FLOOR_MRR = 0.60
FLOOR_HIT_AT_1 = 0.50
FLOOR_HIT_AT_5 = 0.75
FLOOR_REFUSAL_ACCURACY = 0.85
FLOOR_AVG_CONFIDENCE = 0.50
CEILING_AVG_LATENCY_MS = 15000


def _api_alive() -> bool:
    try:
        r = requests.get(f"{API}/health", timeout=3)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False


@pytest.fixture(scope="module")
def eval_summary() -> dict[str, float]:
    if not _api_alive():
        pytest.skip(f"RAG API недоступен на {API}; gate запускается только когда API up")
    from eval_retrieval import GOLDEN_QUESTIONS, evaluate_one, summarize

    rows = [evaluate_one(API, item) for item in GOLDEN_QUESTIONS]
    summary = summarize(rows)
    print("\n=== Eval gate summary ===")
    for k, v in summary.items():
        print(f"  {k}: {v}")
    return summary


def test_mrr_above_floor(eval_summary: dict[str, float]) -> None:
    assert eval_summary["mrr"] >= FLOOR_MRR, (
        f"MRR={eval_summary['mrr']} ниже floor={FLOOR_MRR}. "
        "Retrieval quality деградировала. Проверь corpus changes, hybrid weights, embedding model."
    )


def test_hit_at_1_above_floor(eval_summary: dict[str, float]) -> None:
    assert eval_summary["hit@1"] >= FLOOR_HIT_AT_1, (
        f"Hit@1={eval_summary['hit@1']} ниже floor={FLOOR_HIT_AT_1}. "
        "Top-1 retrieval ухудшился."
    )


def test_hit_at_5_above_floor(eval_summary: dict[str, float]) -> None:
    assert eval_summary["hit@5"] >= FLOOR_HIT_AT_5, (
        f"Hit@5={eval_summary['hit@5']} ниже floor={FLOOR_HIT_AT_5}."
    )


def test_refusal_accuracy_above_floor(eval_summary: dict[str, float]) -> None:
    assert eval_summary["refusal_accuracy"] >= FLOOR_REFUSAL_ACCURACY, (
        f"Refusal accuracy={eval_summary['refusal_accuracy']} ниже floor={FLOOR_REFUSAL_ACCURACY}. "
        "Бот стал чаще отказывать там, где должен отвечать, или наоборот — отвечать там, где нет данных."
    )


def test_avg_confidence_above_floor(eval_summary: dict[str, float]) -> None:
    assert eval_summary["avg_confidence"] >= FLOOR_AVG_CONFIDENCE, (
        f"Avg confidence={eval_summary['avg_confidence']} ниже floor={FLOOR_AVG_CONFIDENCE}. "
        "Большинство ответов идёт с низкой уверенностью — content или retrieval gap."
    )


def test_latency_under_ceiling(eval_summary: dict[str, float]) -> None:
    assert eval_summary["avg_latency_ms"] <= CEILING_AVG_LATENCY_MS, (
        f"Avg latency={eval_summary['avg_latency_ms']}ms превысил ceiling={CEILING_AVG_LATENCY_MS}ms. "
        "Mistral 429 / network / cold start."
    )


def test_baseline_file_committed() -> None:
    """`eval/baseline.json` закоммичен в репо вместе с floor'ами, чтобы diff показывал
    что именно изменилось. (`.tmp/eval_baseline.json` — рабочая копия, gitignored.)"""
    baseline = ROOT / "eval" / "baseline.json"
    assert baseline.exists(), (
        f"Eval baseline {baseline} не существует. Запусти "
        "`python scripts/eval_retrieval.py --output eval/baseline.json`."
    )
    data = json.loads(baseline.read_text(encoding="utf-8"))
    assert data["summary"]["mrr"] >= FLOOR_MRR, (
        "Saved baseline MRR ниже floor — кто-то закоммитил регрессию в baseline."
    )
