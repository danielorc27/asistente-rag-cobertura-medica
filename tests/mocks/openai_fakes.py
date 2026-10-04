"""Clientes OpenAI simulados para pruebas (§11.4: nunca OpenAI real)."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class _FakeMessage:
    content: str | None


@dataclass
class _FakeChoice:
    message: _FakeMessage


@dataclass
class _FakeUsage:
    prompt_tokens: int = 100
    completion_tokens: int = 50


@dataclass
class _FakeChatResponse:
    choices: list[_FakeChoice]
    model: str = "gpt-4.1-fake"
    usage: _FakeUsage = field(default_factory=_FakeUsage)


class FakeChatCompletions:
    def __init__(self, reply: str | None) -> None:
        self._reply = reply
        self.last_kwargs: dict[str, Any] = {}

    def create(self, **kwargs: Any) -> _FakeChatResponse:
        self.last_kwargs = kwargs
        return _FakeChatResponse(choices=[_FakeChoice(_FakeMessage(self._reply))])


class FakeOpenAIClient:
    """Simula el subconjunto del SDK usado por OpenAIProvider."""

    def __init__(self, reply: str | None = '{"ok": true}') -> None:
        self.chat = type("Chat", (), {})()
        self.chat.completions = FakeChatCompletions(reply)


@dataclass
class _FakeEmbeddingItem:
    index: int | None
    embedding: list[float]


@dataclass
class _FakeEmbeddingResponse:
    data: list[_FakeEmbeddingItem]


class FakeEmbeddings:
    def __init__(self, dimensions: int = 4, null_index: bool = False) -> None:
        self._dimensions = dimensions
        self._null_index = null_index
        self.calls: list[list[str]] = []

    def create(self, *, model: str, input: list[str]) -> _FakeEmbeddingResponse:  # noqa: A002
        self.calls.append(list(input))
        data = [
            _FakeEmbeddingItem(
                index=None if self._null_index else i,
                embedding=[float(i)] * self._dimensions,
            )
            for i in range(len(input))
        ]
        return _FakeEmbeddingResponse(data=list(reversed(data)))  # desordenado a propósito


class FakeEmbeddingClient:
    def __init__(self, dimensions: int = 4, null_index: bool = False) -> None:
        self.embeddings = FakeEmbeddings(dimensions, null_index)
