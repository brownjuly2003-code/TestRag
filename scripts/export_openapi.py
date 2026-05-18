"""Export OpenAPI schema из FastAPI app в docs/openapi.yaml.

Sprint 6 #2: фиксируем контракт API в репо, чтобы изменения видно было
в diff. Запускать после изменений Pydantic-моделей в rag-api/app/main.py.

CI gate: scripts/test_eval_regression.py-style — re-export и diff против
закоммиченной версии (см. tests/test_openapi_contract.py).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "rag-api"))

import yaml  # noqa: E402
from app.main import app  # noqa: E402


def _write_lf(path: Path, text: str) -> None:
    """CX review b61609d P3: запись с явным LF, чтобы Windows-CRLF не ломал
    `git diff --check` whitespace gate. `Path.write_text` на Windows конвертит
    `\\n` → `\\r\\n` через универсальные newlines; обходим через `write_bytes`."""
    if not text.endswith("\n"):
        text += "\n"
    path.write_bytes(text.encode("utf-8"))


def export(path: Path) -> None:
    schema = app.openapi()
    yaml_text = yaml.safe_dump(schema, sort_keys=False, allow_unicode=True, width=120)
    _write_lf(path, yaml_text)
    print(f"openapi.yaml written: {path}")
    print(f"  paths: {len(schema.get('paths', {}))}")
    print(f"  schemas: {len(schema.get('components', {}).get('schemas', {}))}")


def main() -> int:
    out = REPO_ROOT / "docs" / "openapi.yaml"
    out.parent.mkdir(parents=True, exist_ok=True)
    export(out)
    json_out = REPO_ROOT / "docs" / "openapi.json"
    _write_lf(
        json_out,
        json.dumps(app.openapi(), ensure_ascii=False, indent=2, sort_keys=False),
    )
    print(f"openapi.json written: {json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
