import asyncio

import httpx

from app.llm import MistralChatClient, MistralEmbeddingClient
from app.rag import DocumentChunk, SearchResult


class FailingClient:
    def __init__(self, timeout):
        self.timeout = timeout

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def post(self, *args, **kwargs):
        return httpx.Response(429, request=httpx.Request("POST", "https://api.mistral.ai/v1/embeddings"))


class FailingAsyncClient:
    def __init__(self, timeout):
        self.timeout = timeout

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, *args, **kwargs):
        return httpx.Response(429, request=httpx.Request("POST", "https://api.mistral.ai/v1/embeddings"))


def test_embed_texts_returns_none_embeddings_on_http_error(monkeypatch):
    monkeypatch.setattr("app.llm.httpx.Client", FailingClient)

    client = MistralEmbeddingClient("key", "mistral-embed")

    assert client.embed_texts(["one", "two"]) == [None, None]


def test_embed_query_returns_none_on_http_error(monkeypatch):
    monkeypatch.setattr("app.llm.httpx.AsyncClient", FailingAsyncClient)

    client = MistralEmbeddingClient("key", "mistral-embed")

    assert asyncio.run(client.embed_query("one")) is None


class _StubResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class _StubAsyncClient:
    payload = {
        "choices": [{"message": {"content": "stub answer"}}],
        "usage": {"prompt_tokens": 123, "completion_tokens": 45},
    }

    def __init__(self, timeout):
        self.timeout = timeout

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, *args, **kwargs):
        return _StubResponse(self.payload)


def test_chat_answer_returns_text_and_usage(monkeypatch):
    """LLM.answer теперь возвращает (text, usage) для observability."""
    monkeypatch.setattr("app.llm.httpx.AsyncClient", _StubAsyncClient)
    chunk = DocumentChunk(chunk_id="x", content="text", metadata={"file": "x.md"})
    result = SearchResult(chunk=chunk, bm25_score=0.5, vector_score=0.5, final_score=0.6)
    client = MistralChatClient("key", "mistral-small-latest")
    text, usage = asyncio.run(client.answer("q?", [result]))
    assert text == "stub answer"
    assert usage["prompt_tokens"] == 123
    assert usage["completion_tokens"] == 45
    assert usage["model"] == "mistral-small-latest"


def test_chat_answer_disabled_returns_none_text_with_usage_shape():
    client = MistralChatClient("", "mistral-small-latest")
    text, usage = asyncio.run(client.answer("q?", []))
    assert text is None
    assert usage == {"model": None, "prompt_tokens": None, "completion_tokens": None}
