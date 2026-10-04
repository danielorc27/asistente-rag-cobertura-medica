"""Adapter del LLM sobre el SDK de OpenAI (§3.8, §3.16).

El SDK nunca se expone fuera de este módulo. El cliente puede inyectarse
en pruebas para no depender del servicio real (§11.4).
"""

import logging
import time
from typing import Any

from openai import APIError, OpenAI
from openai.types.chat import ChatCompletionMessageParam

from app.domain.exceptions.errors import LLMProviderError
from app.domain.providers.llm_provider import LLMProvider, LLMRequest, LLMResult

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """Implementación de LLMProvider para modelos GPT de OpenAI."""

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout_seconds: float = 60.0,
        max_retries: int = 2,
        base_url: str = "",
        client: Any | None = None,
    ) -> None:
        self._model = model
        self._api_key = api_key
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries
        # base_url permite apuntar a endpoints compatibles con OpenAI
        # (Ollama local, Gemini, Azure) sin tocar ninguna otra capa (§2.13).
        self._base_url = base_url or None
        # Cliente lazy: el SDK exige credenciales al construirse y la app
        # debe poder arrancar sin API Key (§9.12); el fallo se difiere al uso.
        self._client_instance = client

    @property
    def _client(self) -> Any:
        if self._client_instance is None:
            self._client_instance = OpenAI(
                api_key=self._api_key,
                base_url=self._base_url,
                timeout=self._timeout_seconds,
                max_retries=self._max_retries,
            )
        return self._client_instance

    def generate(self, request: LLMRequest) -> LLMResult:
        started = time.perf_counter()
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": request.system},
            {"role": "user", "content": request.user},
        ]
        try:
            if request.json_output:
                response = self._client.chat.completions.create(
                    model=self._model,
                    messages=messages,
                    response_format={"type": "json_object"},
                )
            else:
                response = self._client.chat.completions.create(
                    model=self._model, messages=messages
                )
        except APIError as exc:
            raise LLMProviderError(f"Fallo del proveedor LLM: {exc}") from exc
        except Exception as exc:  # timeouts/conexión del SDK
            raise LLMProviderError(f"Error de comunicación con el LLM: {exc}") from exc

        latency_ms = (time.perf_counter() - started) * 1000
        choice = response.choices[0] if response.choices else None
        text = (choice.message.content or "") if choice and choice.message else ""
        if not text.strip():
            raise LLMProviderError("El proveedor LLM devolvió una respuesta vacía.")

        usage = getattr(response, "usage", None)
        logger.info(
            "LLM respondió en %.0f ms (modelo=%s, tokens_in=%s, tokens_out=%s).",
            latency_ms,
            response.model,
            getattr(usage, "prompt_tokens", None),
            getattr(usage, "completion_tokens", None),
        )
        return LLMResult(
            text=text,
            model=response.model,
            input_tokens=getattr(usage, "prompt_tokens", None),
            output_tokens=getattr(usage, "completion_tokens", None),
            latency_ms=latency_ms,
        )
