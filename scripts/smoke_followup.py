"""E2E smoke для N1 follow-up: /followup → /ask с crafted question."""
from __future__ import annotations

import json
import sys

import subprocess

import requests

API = "http://localhost:8000"


def fetch_recent_rl() -> tuple[str, str, str] | None:
    sql = (
        "select id::text || '|' || coalesce(telegram_user_id, '') || '|' || "
        "replace(question, chr(10), ' ') "
        "from request_logs "
        "where sources is not null and jsonb_array_length(sources) >= 2 "
        "order by created_at desc limit 1"
    )
    result = subprocess.run(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "postgres",
            "psql",
            "-U",
            "testrag",
            "-d",
            "testrag",
            "-tA",
            "-c",
            sql,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    line = result.stdout.strip()
    if not line:
        return None
    parts = line.split("|", 2)
    if len(parts) != 3:
        return None
    return parts[0], parts[1], parts[2]


def main() -> int:
    rl = fetch_recent_rl()
    if not rl:
        print("FAIL: no request_log with >=2 sources", file=sys.stderr)
        return 1
    rl_id, tg_user, original_q = rl
    print(f"using rl={rl_id}, original Q: {original_q[:80]}")

    # 2. /followup idx=0 and idx=1
    questions: list[str] = []
    for idx in (0, 1):
        r = requests.get(f"{API}/followup", params={"request_log_id": rl_id, "idx": idx}, timeout=10)
        r.raise_for_status()
        body = r.json()
        print(f"  idx={idx}: {body['question'][:100]}")
        print(f"    source: file={body['source']['file']} section={body['source']['section']}")
        questions.append(body["question"])

    # 3. Use first follow-up question against /ask (real RAG run)
    crafted = questions[0]
    r = requests.post(
        f"{API}/ask",
        json={"question": crafted, "telegram_user_id": tg_user, "top_k": 5},
        timeout=120,
    )
    r.raise_for_status()
    ask = r.json()
    print()
    print(f"/ask reply: refused={ask['refused']} conf={ask['confidence']}")
    print(f"  answer (first 200 chars): {ask['answer'][:200]}")
    print(f"  new rl_id: {ask['request_log_id']}")
    print(f"  new sources [{len(ask['sources'])}]:")
    for s in ask["sources"][:5]:
        print(f"    - {s['file']} ({s['section']}, score {s['score']})")

    # 4. Verify a NEW follow-up resolves on the freshly-created rl
    new_rl = ask["request_log_id"]
    r = requests.get(f"{API}/followup", params={"request_log_id": new_rl, "idx": 0}, timeout=10)
    r.raise_for_status()
    print()
    print(f"recursive /followup on new rl idx=0: {r.json()['question'][:100]}")

    # 5. Negative cases
    r = requests.get(f"{API}/followup", params={"request_log_id": "not-a-uuid", "idx": 0}, timeout=10)
    assert r.status_code == 404, f"expected 404, got {r.status_code}"
    r = requests.get(f"{API}/followup", params={"request_log_id": rl_id, "idx": 99}, timeout=10)
    assert r.status_code == 400, f"expected 400 (idx>9), got {r.status_code}"
    r = requests.get(f"{API}/followup", params={"request_log_id": rl_id, "idx": 7}, timeout=10)
    assert r.status_code == 404, f"expected 404 (out of range), got {r.status_code}"
    r = requests.get(f"{API}/followup", params={"request_log_id": rl_id, "idx": -1}, timeout=10)
    assert r.status_code == 400, f"expected 400, got {r.status_code}"
    print("\nnegative cases: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
