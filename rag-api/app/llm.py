from __future__ import annotations

import json

import httpx

from .rag import SearchResult


class MistralChatClient:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    async def answer(self, question: str, results: list[SearchResult]) -> str | None:
        if not self.enabled:
            return None

        context = "\n\n".join(
            f"Источник {index + 1}: {result.chunk.content}"
            for index, result in enumerate(results[:5])
            if result.final_score > 0
        )
        if not context:
            return None

        payload = {
            "model": self.model,
            "temperature": 0.1,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Ты юридический и HR RAG-ассистент. Отвечай только по переданным источникам. "
                        "Если источников недостаточно, скажи, что данных недостаточно."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Вопрос: {question}\n\nИсточники:\n{context}",
                },
            ],
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        return data["choices"][0]["message"]["content"]

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

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        return _loads_json_object(content)


class MistralEmbeddingClient:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def embed_texts(self, texts: list[str]) -> list[list[float] | None]:
        if not self.enabled or not texts:
            return [None for _ in texts]

        payload = {"model": self.model, "input": texts}
        with httpx.Client(timeout=30) as client:
            response = client.post(
                "https://api.mistral.ai/v1/embeddings",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        embeddings = [item["embedding"] for item in data.get("data", [])]
        return embeddings + [None for _ in range(max(0, len(texts) - len(embeddings)))]

    async def embed_query(self, text: str) -> list[float] | None:
        if not self.enabled:
            return None

        payload = {"model": self.model, "input": text}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.mistral.ai/v1/embeddings",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        items = data.get("data", [])
        return items[0]["embedding"] if items else None


def _loads_json_object(content: str) -> dict | None:
    stripped = content.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if stripped.startswith("json"):
            stripped = stripped[4:].strip()
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end < start:
        return None
    return json.loads(stripped[start : end + 1])
