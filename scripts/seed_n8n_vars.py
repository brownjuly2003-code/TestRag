"""Seed n8n.variables.TELEGRAM_BOT_TOKEN for clean-DB onboarding.

n8n's UI gates variable create on Enterprise license (`isVariablesEnabled`), but
the read path (`getAllCached` → `$vars` proxy) works in Community Edition once a
row exists. We bypass the UI by inserting directly via SQL.

Required after fresh `docker compose down -v` / new postgres volume. Idempotent:
re-runs upsert existing key. Restart n8n afterwards so the variable cache reloads.

Usage:
    python scripts/seed_n8n_vars.py
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import uuid

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENV = ROOT / ".env"
POSTGRES_CONTAINER = "testrag-postgres-1"


def _read_token() -> str:
    if not ENV.exists():
        raise SystemExit(f"missing {ENV}")
    match = re.search(r"^TELEGRAM_BOT_TOKEN=(\S+)$", ENV.read_text(encoding="utf-8"), flags=re.MULTILINE)
    if not match:
        raise SystemExit("TELEGRAM_BOT_TOKEN not found in .env")
    return match.group(1)


def _build_sql(token: str) -> str:
    if "'" in token or "\\" in token:
        raise SystemExit("token contains characters that need escaping; refusing")
    return (
        f"INSERT INTO n8n.variables (id, key, type, value) "
        f"VALUES ('{uuid.uuid4()}', 'TELEGRAM_BOT_TOKEN', 'string', '{token}') "
        f'ON CONFLICT (key) WHERE "projectId" IS NULL '
        f"DO UPDATE SET value = EXCLUDED.value;"
    )


def main() -> int:
    token = _read_token()
    sql = _build_sql(token)
    proc = subprocess.run(
        ["docker", "exec", "-i", POSTGRES_CONTAINER, "psql", "-U", "testrag", "-d", "testrag", "-v", "ON_ERROR_STOP=1"],
        input=sql,
        text=True,
        capture_output=True,
    )
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    if proc.returncode != 0:
        return proc.returncode
    print("seeded n8n.variables.TELEGRAM_BOT_TOKEN — restart n8n so the cache reloads", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
