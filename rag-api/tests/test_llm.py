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


class _EmptyChoicesAsyncClient(_StubAsyncClient):
    payload = {"choices": [], "usage": {}}


class _MalformedChoiceAsyncClient(_StubAsyncClient):
    payload = {"choices": [{"message": None}]}


class _InvalidJsonAsyncClient(_StubAsyncClient):
    async def post(self, *args, **kwargs):
        class BadJsonResponse:
            def raise_for_status(self_inner):
                return None

            def json(self_inner):
                raise ValueError("not valid json")

        return BadJsonResponse()


def test_chat_answer_handles_empty_choices(monkeypatch):
    """Sprint 5 #4 / codex-audit#2.3: пустой choices не должен ронять 500.
    `_extract_choice_content` возвращает None, answer возвращает (None, usage)."""
    monkeypatch.setattr("app.llm.httpx.AsyncClient", _EmptyChoicesAsyncClient)
    client = MistralChatClient("key", "mistral-small-latest")
    chunk = DocumentChunk(chunk_id="x", content="text", metadata={"file": "x.md"})
    result = SearchResult(chunk=chunk, bm25_score=0.5, vector_score=0.5, final_score=0.6)
    text, usage = asyncio.run(client.answer("q?", [result]))
    assert text is None
    assert usage["model"] == "mistral-small-latest"


def test_chat_answer_handles_malformed_message(monkeypatch):
    monkeypatch.setattr("app.llm.httpx.AsyncClient", _MalformedChoiceAsyncClient)
    client = MistralChatClient("key", "mistral-small-latest")
    chunk = DocumentChunk(chunk_id="x", content="text", metadata={"file": "x.md"})
    result = SearchResult(chunk=chunk, bm25_score=0.5, vector_score=0.5, final_score=0.6)
    text, usage = asyncio.run(client.answer("q?", [result]))
    assert text is None


def test_chat_answer_handles_invalid_json_response(monkeypatch):
    monkeypatch.setattr("app.llm.httpx.AsyncClient", _InvalidJsonAsyncClient)
    client = MistralChatClient("key", "mistral-small-latest")
    chunk = DocumentChunk(chunk_id="x", content="text", metadata={"file": "x.md"})
    result = SearchResult(chunk=chunk, bm25_score=0.5, vector_score=0.5, final_score=0.6)
    text, usage = asyncio.run(client.answer("q?", [result]))
    assert text is None


def test_document_plan_handles_malformed_json():
    """Sprint 5 #4 / codex-audit#7.3: невалидный JSON в LLM-ответе на document plan не должен крашить."""
    from app.llm import _loads_json_object

    assert _loads_json_object("{ broken : json }") is None
    assert _loads_json_object("```json\n{}\n```") == {}
    assert _loads_json_object("без JSON-объекта") is None


def test_embedding_dim_mismatch_logs_warning(caplog):
    """Sprint 5 #4 / codex-audit#6.2: смена embedding модели/dim не должна тихо ронять cosine в 0."""
    import logging
    client = MistralEmbeddingClient("key", "mistral-embed")
    client._check_dim([0.1] * 1024)
    assert client.observed_dim == 1024
    with caplog.at_level(logging.WARNING, logger="app.llm"):
        client._check_dim([0.1] * 768)
    assert any("dim_mismatch" in rec.message for rec in caplog.records)
