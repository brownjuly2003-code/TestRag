from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path


def _default_docs_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "sample_docs"


@dataclass(frozen=True)
class Settings:
    docs_path: Path
    docs_manifest_path: Path | None
    min_confidence: float
    database_url: str
    mistral_api_key: str
    mistral_chat_model: str
    mistral_embedding_model: str
    allowed_telegram_user_ids_raw: str


@lru_cache
def get_settings() -> Settings:
    docs_manifest_path = os.getenv("DOCS_MANIFEST_PATH", "").strip()
    return Settings(
        docs_path=Path(os.getenv("DOCS_PATH", str(_default_docs_path()))),
        docs_manifest_path=Path(docs_manifest_path) if docs_manifest_path else None,
        min_confidence=float(os.getenv("MIN_CONFIDENCE", "0.25")),
        database_url=os.getenv("DATABASE_URL", ""),
        mistral_api_key=os.getenv("MISTRAL_API_KEY", ""),
        mistral_chat_model=os.getenv("MISTRAL_CHAT_MODEL", "mistral-small-latest"),
        mistral_embedding_model=os.getenv("MISTRAL_EMBEDDING_MODEL", "mistral-embed"),
        allowed_telegram_user_ids_raw=os.getenv("ALLOWED_TELEGRAM_USER_IDS", ""),
    )
