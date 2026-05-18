from __future__ import annotations

import json
import logging

import httpx

from .rag import SearchResult

logger = logging.getLogger(__name__)


def _extract_choice_content(data: object) -> str | None:
    """Sprint 5 #4 (codex-audit#2.3): guard `data['choices'][0]['message']['content']`
    индексацию. Mistral / OpenAI могут вернуть пустой `choices`, отсутствующий
    `message`, тип `None` — раньше падало `KeyError`/`IndexError` в 500."""
    if not isinstance(data, dict):
        return None
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices:
        return None
    first = choices[0]
    if not isinstance(first, dict):
        return None
    message = first.get("message")
    if not isinstance(message, dict):
        return None
    content = message.get("content")
    return content if isinstance(content, str) else None


class MistralChatClient:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model
        # Sprint 6 #5 (codex-audit MISSED#8.3): singleton AsyncClient вместо
        # per-request new socket — переиспользует TCP/TLS handshake.
        self._async_client: httpx.AsyncClient | None = None

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def _get_async_client(self) -> httpx.AsyncClient:
        if self._async_client is None or self._async_client.is_closed:
            self._async_client = httpx.AsyncClient(timeout=30)
        return self._async_client

    async def aclose(self) -> None:
        if self._async_client is not None and not self._async_client.is_closed:
            await self._async_client.aclose()

    async def answer(
        self, question: str, results: list[SearchResult]
    ) -> tuple[str | None, dict[str, int | str | None]]:
        usage: dict[str, int | str | None] = {
            "model": self.model if self.enabled else None,
            "prompt_tokens": None,
            "completion_tokens": None,
        }
        if not self.enabled:
            return None, usage

        context = "\n\n".join(
            f"Источник {index + 1}: {result.chunk.content}"
            for index, result in enumerate(results[:5])
            if result.final_score > 0
        )
        if not context:
            return None, usage

        payload = {
            "model": self.model,
            "temperature": 0.1,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Ты юридический и HR RAG-ассистент. Отвечай только по переданным источникам. "
                        "Если источников недостаточно, скажи, что данных недостаточно. "
                        # Sprint 8 #2 (codex-audit#2.2): просим Mistral маркировать
                        # факты source-id'ом для проверяемости. UI всё равно показывает
                        # отдельный блок «Источники:», но inline-маркеры дают пользователю
                        # явную привязку утверждения → документ.
                        "Когда ссылаешься на факт, указывай источник в формате [Источник N] "
                        "(N — номер из переданного списка). Не выдумывай номера, "
                        "не ссылайся на источники, которых не было в контексте."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Вопрос: {question}\n\nИсточники:\n{context}",
                },
            ],
        }

        try:
            client = self._get_async_client()
            response = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as exc:
            logger.warning("mistral.chat http_error endpoint=chat/completions error=%s", exc)
            return None, usage
        except ValueError as exc:
            logger.warning("mistral.chat invalid_json endpoint=chat/completions error=%s", exc)
            return None, usage

        api_usage = data.get("usage", {}) or {}
        usage["prompt_tokens"] = api_usage.get("prompt_tokens")
        usage["completion_tokens"] = api_usage.get("completion_tokens")
        content = _extract_choice_content(data)
        if content is None:
            logger.warning("mistral.chat empty_choices model=%s", self.model)
        return content, usage

    async def document_plan(self, system_prompt: str, user_prompt: str) -> dict | None:
        if not self.enabled:
            return None

        payload = {
            "model": self.model,
            "temperature": 0.1,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        try:
            client = self._get_async_client()
            response = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as exc:
            logger.warning("mistral.doc_plan http_error error=%s", exc)
            return None
        except ValueError as exc:
            logger.warning("mistral.doc_plan invalid_json error=%s", exc)
            return None

        content = _extract_choice_content(data)
        if content is None:
            return None
        return _loads_json_object(content)


class MistralEmbeddingClient:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model
        # Sprint 5 #4 (codex-audit#6.2): pin embedding dim после первого успешного вызова —
        # подменили модель → log warning при первом несовпадении.
        self._observed_dim: int | None = None
        # Sprint 6 #5: singleton AsyncClient для embed_query hot-path в /ask.
        # embed_texts (sync) остаётся per-call — вызывается только в ingest на startup.
        self._async_client: httpx.AsyncClient | None = None

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def _get_async_client(self) -> httpx.AsyncClient:
        if self._async_client is None or self._async_client.is_closed:
            self._async_client = httpx.AsyncClient(timeout=30)
        return self._async_client

    async def aclose(self) -> None:
        if self._async_client is not None and not self._async_client.is_closed:
            await self._async_client.aclose()

    @property
    def observed_dim(self) -> int | None:
        return self._observed_dim

    def _check_dim(self, vec: list[float] | None) -> None:
        if not isinstance(vec, list) or not vec:
            return
        if self._observed_dim is None:
            self._observed_dim = len(vec)
            return
        if len(vec) != self._observed_dim:
            logger.warning(
                "mistral.embed dim_mismatch expected=%s actual=%s model=%s — "
                "vector likely drops to cosine=0 silently",
                self._observed_dim,
                len(vec),
                self.model,
            )

    def embed_texts(self, texts: list[str]) -> list[list[float] | None]:
        if not self.enabled or not texts:
            return [None for _ in texts]

        payload = {"model": self.model, "input": texts}
        try:
            with httpx.Client(timeout=30) as client:
                response = client.post(
                    "https://api.mistral.ai/v1/embeddings",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            logger.warning("mistral.embed http_error endpoint=embeddings batch=%d error=%s", len(texts), exc)
            return [None for _ in texts]
        except ValueError as exc:
            logger.warning("mistral.embed invalid_json batch=%d error=%s", len(texts), exc)
            return [None for _ in texts]

        items = data.get("data", []) if isinstance(data, dict) else []
        embeddings: list[list[float] | None] = []
        for item in items:
            vec = item.get("embedding") if isinstance(item, dict) else None
            self._check_dim(vec)
            embeddings.append(vec if isinstance(vec, list) else None)
        return embeddings + [None for _ in range(max(0, len(texts) - len(embeddings)))]

    async def embed_query(self, text: str) -> list[float] | None:
        if not self.enabled:
            return None

        payload = {"model": self.model, "input": text}
        try:
            client = self._get_async_client()
            response = await client.post(
                "https://api.mistral.ai/v1/embeddings",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as exc:
            logger.warning("mistral.embed_query http_error error=%s", exc)
            return None
        except ValueError as exc:
            logger.warning("mistral.embed_query invalid_json error=%s", exc)
            return None

        items = data.get("data", []) if isinstance(data, dict) else []
        if not items:
            return None
        first = items[0]
        vec = first.get("embedding") if isinstance(first, dict) else None
        if not isinstance(vec, list):
            return None
        self._check_dim(vec)
        return vec


def _loads_json_object(content: str) -> dict | None:
    """Sprint 5 #4 (codex-audit#7.3): catch JSONDecodeError, верни None — раньше
    падало 500 при невалидном JSON в LLM-ответе на document plan."""
    stripped = content.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if stripped.startswith("json"):
            stripped = stripped[4:].strip()
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end < start:
        return None
    try:
        return json.loads(stripped[start : end + 1])
    except json.JSONDecodeError as exc:
        logger.warning("mistral.doc_plan json_decode_error error=%s payload_head=%r", exc, stripped[:120])
        return None
