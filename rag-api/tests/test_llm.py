import asyncio

import httpx

from app.llm import MistralEmbeddingClient


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
