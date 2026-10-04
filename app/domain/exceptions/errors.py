"""Jerarquía de errores del dominio (§9.11)."""


class DomainError(Exception):
    """Base de todos los errores del dominio."""


class ConfigurationError(DomainError):
    """Configuración faltante o inválida."""


class AffiliateNotFoundError(DomainError):
    """El afiliado consultado no existe en el repositorio."""

    def __init__(self, affiliate_id: str) -> None:
        super().__init__(f"Afiliado no encontrado: {affiliate_id}")
        self.affiliate_id = affiliate_id


class DocumentLoadError(DomainError):
    """Un documento no pudo leerse o está corrupto."""


class AffiliateDataError(DomainError):
    """Un registro de afiliado contiene valores inválidos o inconsistentes."""


class IndexInvalidError(DomainError):
    """El índice vectorial no existe o es incompatible con la configuración."""


class LLMProviderError(DomainError):
    """Fallo al comunicarse con el proveedor LLM."""


class EmbeddingProviderError(DomainError):
    """Fallo al generar embeddings."""


class ResponseValidationError(DomainError):
    """La respuesta del LLM no supera las validaciones (§7.12)."""
