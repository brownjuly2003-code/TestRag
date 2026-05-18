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

# Каждый item: question + expected_files (список substrings — любое попадание = hit), optional
# expected_section, optional expected_refused (если True, ожидаем status='unanswerable').
# Список вместо одного substring: после Sprint 5 content enrichment один термин может корректно
# находиться И в 07_faq_expedition (глоссарий), И в 05_tlog/06_comp (профильный регламент).
GOLDEN_QUESTIONS: list[dict[str, Any]] = [
    {
        "q": "Что такое controlled zone?",
        "expected_files": ["01_hr_pol_safety", "07_faq_expedition"],
        "expected_refused": False,
    },
    {
        "q": "Какие документы нужны для отправки dangerous goods авиатранспортом?",
        "expected_files": ["06_comp", "05_tlog_regulation_dangerous_goods", "07_faq_expedition"],
        "expected_refused": False,
    },
    {
        "q": "Какие основания для досрочного расторжения трудового договора?",
        "expected_files": ["07_faq_dismissal", "03_legal_contract_termination"],
        "expected_refused": False,
    },
    {
        "q": "Что такое AWB и MAWB?",
        "expected_files": ["05_tlog", "07_faq_expedition"],
        "expected_refused": False,
    },
    {
        "q": "Какой испытательный срок по ТК РФ?",
        "expected_files": ["01_hr_probation", "07_faq_probation"],
        "expected_refused": False,
    },
    {
        "q": "Какой максимальный размер ULD для авиаперевозки?",
        "expected_files": ["05_tlog", "07_faq_expedition"],
        "expected_refused": False,
    },
    {
        "q": "Как составить претензию контрагенту?",
        "expected_files": ["04_legal_cla", "07_faq_claims_procedure"],
        "expected_refused": False,
    },
    {
        "q": "Какие правила для cutoff time в авиагрузовых перевозках?",
        "expected_files": ["05_tlog", "07_faq_expedition"],
        "expected_refused": False,
    },
    # Off-corpus refusal: тематика которой нет в базе.
    {
        "q": "Какие документы нужны для отправки лития морем?",
        "expected_files": [],
        "expected_refused": True,
    },
    {
        "q": "Что такое GHA?",
        "expected_files": ["05_tlog", "07_faq_expedition"],
        "expected_refused": False,
    },
    # --- Sprint 7 golden expansion 10 → 30: HR/legal/transport/compliance coverage ---
    {
        "q": "Какие условия для удалённой работы по локальному регламенту?",
        "expected_files": ["01_hr_pol_remote_work", "02_hr_tmp_remote_work"],
        "expected_refused": False,
    },
    {
        "q": "Какие выплаты положены при увольнении по соглашению сторон?",
        "expected_files": ["07_faq_dismissal", "01_hr_dismissal_procedure"],
        "expected_refused": False,
    },
    {
        "q": "Можно ли продлить испытательный срок по ст. 70 ТК РФ?",
        "expected_files": ["01_hr_probation_procedure", "07_faq_probation", "external_tk_rf_chapter_11"],
        "expected_refused": False,
    },
    {
        "q": "Какие сроки командировки и условия по суточным?",
        "expected_files": ["01_hr_pol_business_trip"],
        "expected_refused": False,
    },
    {
        "q": "Что входит в персональные данные по политике компании?",
        "expected_files": ["06_comp_policy_pdp", "07_faq_pdp"],
        "expected_refused": False,
    },
    {
        "q": "Какой срок ответа на претензию по поставке?",
        # Срок ответа на претензию документируется и в FAQ, и в самом договоре поставки.
        "expected_files": ["07_faq_claims_procedure", "04_legal_claim_late_delivery", "03_legal_contract_supply_goods"],
        "expected_refused": False,
    },
    {
        "q": "Что делать при инциденте с утечкой персональных данных?",
        "expected_files": ["06_comp_policy_incident_response"],
        "expected_refused": False,
    },
    {
        "q": "Сколько часов в смену может работать водитель?",
        "expected_files": ["05_tlog_policy_driver_hours"],
        "expected_refused": False,
    },
    {
        "q": "Какие документы оформляются при таможенной очистке?",
        "expected_files": ["05_tlog_regulation_customs_clearance", "03_legal_contract_customs_broker"],
        "expected_refused": False,
    },
    {
        "q": "Какие штрафные санкции за просрочку поставки товара?",
        "expected_files": ["04_legal_claim_late_delivery", "03_legal_contract_supply_goods"],
        "expected_refused": False,
    },
    {
        "q": "Какие обязательные реквизиты должна содержать транспортная накладная?",
        "expected_files": ["05_tlog_regulation_waybill"],
        "expected_refused": False,
    },
    {
        "q": "Каков порядок действий при harassment на рабочем месте?",
        "expected_files": ["01_hr_pol_harassment"],
        "expected_refused": False,
    },
    {
        "q": "Как оформить дополнительное соглашение к трудовому договору?",
        "expected_files": ["02_hr_tmp_add_agreement", "02_hr_tmp_employment_contract"],
        "expected_refused": False,
    },
    {
        "q": "Сколько лет хранятся персональные данные сотрудников?",
        # FAQ по PDP суммирует политику retention; data_retention/pdp policy — первичный источник.
        "expected_files": ["06_comp_policy_data_retention", "06_comp_policy_pdp", "07_faq_pdp"],
        "expected_refused": False,
    },
    {
        "q": "Какие документы нужны для автоперевозки опасных грузов?",
        "expected_files": ["05_tlog_regulation_dangerous_goods", "05_tlog_contract_transport_road"],
        "expected_refused": False,
    },
    {
        "q": "Какие условия конфиденциальности обязан соблюдать сотрудник?",
        # NDA-клаузы лежат в трудовом договоре наряду с conf-policy и политикой по комм. тайне.
        "expected_files": [
            "01_hr_pol_confidentiality_emp",
            "06_comp_policy_commercial_secret",
            "02_hr_tmp_employment_contract",
        ],
        "expected_refused": False,
    },
    # Off-corpus refusals: налоги / визы / стандарты / курсы валют — не входят в корпус.
    {
        "q": "Какая ставка НДФЛ для резидентов в 2026 году?",
        "expected_files": [],
        "expected_refused": True,
    },
    {
        "q": "Как оформить шенгенскую визу для сотрудника?",
        "expected_files": [],
        "expected_refused": True,
    },
    {
        "q": "Какие требования по сертификации ISO 9001?",
        "expected_files": [],
        "expected_refused": True,
    },
    {
        "q": "Какой курс рубля к евро на сегодня?",
        "expected_files": [],
        "expected_refused": True,
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
    expected_files: list[str] = item.get("expected_files") or []
    sources = response.get("sources") or []
    files = [s.get("file") or "" for s in sources]

    hit_at_1 = 0
    hit_at_5 = 0
    rank = None
    if expected_files:
        for idx, fname in enumerate(files):
            if any(exp in fname for exp in expected_files):
                hit_at_5 = 1
                if idx == 0:
                    hit_at_1 = 1
                rank = idx + 1
                break

    refused = response.get("refused", False)
    refusal_correct = refused == item.get("expected_refused", False)

    return {
        "q": item["q"],
        "expected_files": expected_files,
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
        # Write LF + trailing newline (Windows default would emit CRLF and break git pre-commit whitespace gate).
        payload = json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=2) + "\n"
        args.output.write_bytes(payload.encode("utf-8").replace(b"\r\n", b"\n"))
        print(f"\nSaved to {args.output}")

    # Exit code: 1 если хоть один gate пробит. Floor полностью синхронизирован с
    # scripts/test_eval_regression.py: MRR ≥0.60, Hit@1 ≥0.50, Hit@5 ≥0.75,
    # refusal ≥0.85, avg_conf ≥0.50, avg_latency ≤15000ms.
    if (
        summary["mrr"] < 0.60
        or summary["hit@1"] < 0.50
        or summary["hit@5"] < 0.75
        or summary["refusal_accuracy"] < 0.85
        or summary["avg_confidence"] < 0.50
        or summary["avg_latency_ms"] > 15000
    ):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
