"""Factories de proveedores (§3.15).

Permiten cambiar de implementación mediante configuración sin tocar
Application ni Domain. Un proveedor desconocido produce
ConfigurationError con las opciones disponibles.
"""

from app.config.settings import Settings
from app.domain.exceptions.errors import ConfigurationError
from app.domain.providers.chunk_strategy import ChunkStrategy
from app.domain.providers.document_loader import DocumentLoader
from app.domain.providers.embedding_provider import EmbeddingProvider
from app.domain.providers.llm_provider import LLMProvider
from app.domain.providers.vector_store import VectorStore
from app.domain.repositories.affiliate_repository import AffiliateRepository
from app.domain.repositories.index_state_repository import IndexStateRepository
from app.infrastructure.chunking.recursive_chunk_strategy import RecursiveChunkStrategy
from app.infrastructure.document_loader.word_document_loader import WordDocumentLoader
from app.infrastructure.embeddings.mock_embedding_provider import MockEmbeddingProvider
from app.infrastructure.embeddings.openai_embedding_provider import OpenAIEmbeddingProvider
from app.infrastructure.llm.mock_llm_provider import MockLLMProvider
from app.infrastructure.llm.openai_provider import OpenAIProvider
from app.infrastructure.persistence.json_index_state_repository import JsonIndexStateRepository
from app.infrastructure.repositories.excel_affiliate_repository import ExcelAffiliateRepository
from app.infrastructure.vectorstore.chroma_vector_store import ChromaVectorStore

_MANIFEST_FILENAME = "index_manifest.json"


def create_llm_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "openai":
        # OPENAI_BASE_URL permite endpoints compatibles: Ollama, Gemini, Azure.
        return OpenAIProvider(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            timeout_seconds=settings.llm_timeout_seconds,
            max_retries=settings.llm_max_retries,
            base_url=settings.openai_base_url,
        )
    if settings.llm_provider == "mock":
        return MockLLMProvider()
    raise ConfigurationError(
        f"LLM_PROVIDER desconocido: '{settings.llm_provider}'. Disponibles: openai, mock."
    )


def create_embedding_provider(settings: Settings) -> EmbeddingProvider:
    if settings.embedding_provider == "openai":
        return OpenAIEmbeddingProvider(
            api_key=settings.openai_api_key,
            model=settings.embedding_model,
            timeout_seconds=settings.llm_timeout_seconds,
            max_retries=settings.llm_max_retries,
            base_url=settings.openai_base_url,
        )
    if settings.embedding_provider == "mock":
        return MockEmbeddingProvider()
    raise ConfigurationError(
        f"EMBEDDING_PROVIDER desconocido: '{settings.embedding_provider}'. "
        "Disponibles: openai, mock."
    )


def create_vector_store(settings: Settings) -> VectorStore:
    if settings.vector_store_provider == "chroma":
        return ChromaVectorStore(persist_path=settings.vector_db_path)
    raise ConfigurationError(
        f"VECTOR_STORE_PROVIDER desconocido: '{settings.vector_store_provider}'. "
        "Disponibles: chroma."
    )


def create_document_loaders(settings: Settings) -> list[DocumentLoader]:  # noqa: ARG001
    """Loaders disponibles; agregar formatos = agregar loaders (§6.21)."""
    return [WordDocumentLoader()]


def create_chunk_strategy(settings: Settings) -> ChunkStrategy:
    return RecursiveChunkStrategy(
        chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap
    )


def create_affiliate_repository(settings: Settings) -> AffiliateRepository:
    return ExcelAffiliateRepository(file_path=settings.affiliates_file)


def create_index_state_repository(settings: Settings) -> IndexStateRepository:
    return JsonIndexStateRepository(manifest_path=settings.vector_db_path / _MANIFEST_FILENAME)
