"""Manejo centralizado de errores HTTP (§9.11).

Clasifica los errores del dominio en códigos HTTP con mensajes claros.
Nunca expone detalles internos (stack traces, rutas, SDKs) al cliente.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.exceptions.errors import (
    AffiliateDataError,
    AffiliateNotFoundError,
    ConfigurationError,
    DomainError,
    EmbeddingProviderError,
    LLMProviderError,
    ResponseValidationError,
)

logger = logging.getLogger(__name__)

_ERROR_MAP: list[tuple[type[DomainError], int, str]] = [
    (AffiliateNotFoundError, 404, "affiliate_not_found"),
    (AffiliateDataError, 500, "affiliate_data_error"),
    (ResponseValidationError, 502, "llm_response_invalid"),
    (LLMProviderError, 502, "llm_provider_error"),
    (EmbeddingProviderError, 502, "embedding_provider_error"),
    (ConfigurationError, 503, "configuration_error"),
]


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
        for error_type, status_code, category in _ERROR_MAP:
            if isinstance(exc, error_type):
                logger.error("[%s] %s %s: %s", category, request.method, request.url.path, exc)
                app.state.metrics.record_error(category)
                return JSONResponse(
                    status_code=status_code,
                    content={"error": category, "detail": str(exc)},
                )
        logger.exception("Error de dominio no clasificado en %s", request.url.path)
        app.state.metrics.record_error("domain_error")
        return JSONResponse(
            status_code=500,
            content={"error": "domain_error", "detail": "Error interno del dominio."},
        )
