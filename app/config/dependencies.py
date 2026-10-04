"""Composition root del sistema (§14.3).

Único módulo autorizado a importar de todas las capas para cablear
implementaciones concretas (Infrastructure) contra los contratos del
dominio. Las capas Presentation y Application reciben aquí sus
dependencias ya construidas.
"""

from functools import cached_property

from app.application.reasoning.evidence_evaluator import EvidenceEvaluator
from app.application.reasoning.knowledge_retriever import KnowledgeRetriever
from app.application.reasoning.reasoning_engine import ReasoningEngine
from app.application.reasoning.response_validator import ResponseValidator
from app.application.services.indexing_service import IndexingService
from app.application.use_cases.analyze_coverage_use_case import AnalyzeCoverageUseCase
from app.config.settings import Settings, get_settings
from app.domain.providers.chunk_strategy import ChunkStrategy
from app.domain.providers.document_loader import DocumentLoader
from app.domain.providers.embedding_provider import EmbeddingProvider
from app.domain.providers.llm_provider import LLMProvider
from app.domain.providers.text_normalizer import TextNormalizer
from app.domain.providers.vector_store import VectorStore
from app.domain.repositories.affiliate_repository import AffiliateRepository
from app.domain.repositories.index_state_repository import IndexStateRepository
from app.domain.services.eligibility_rules import EligibilityRules
from app.infrastructure.factories.provider_factories import (
    create_affiliate_repository,
    create_chunk_strategy,
    create_document_loaders,
    create_embedding_provider,
    create_index_state_repository,
    create_llm_provider,
    create_vector_store,
)
from app.infrastructure.parser.text_normalizer import DefaultTextNormalizer


class Container:
    """Contenedor simple de dependencias del proceso.

    Construye cada dependencia una sola vez (lazy) y la expone tipada.
    Se prefiere un contenedor explícito sobre un framework de DI para
    mantener las dependencias visibles y fáciles de reemplazar en tests.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    @cached_property
    def llm_provider(self) -> LLMProvider:
        return create_llm_provider(self.settings)

    @cached_property
    def embedding_provider(self) -> EmbeddingProvider:
        return create_embedding_provider(self.settings)

    @cached_property
    def vector_store(self) -> VectorStore:
        return create_vector_store(self.settings)

    @cached_property
    def document_loaders(self) -> list[DocumentLoader]:
        return create_document_loaders(self.settings)

    @cached_property
    def chunk_strategy(self) -> ChunkStrategy:
        return create_chunk_strategy(self.settings)

    @cached_property
    def text_normalizer(self) -> TextNormalizer:
        return DefaultTextNormalizer()

    @cached_property
    def affiliate_repository(self) -> AffiliateRepository:
        return create_affiliate_repository(self.settings)

    @cached_property
    def index_state_repository(self) -> IndexStateRepository:
        return create_index_state_repository(self.settings)

    @cached_property
    def eligibility_rules(self) -> EligibilityRules:
        return EligibilityRules()

    @cached_property
    def knowledge_retriever(self) -> KnowledgeRetriever:
        return KnowledgeRetriever(
            embedding_provider=self.embedding_provider,
            vector_store=self.vector_store,
            top_k=self.settings.top_k_results,
            min_similarity=self.settings.min_similarity_score,
        )

    @cached_property
    def reasoning_engine(self) -> ReasoningEngine:
        return ReasoningEngine(
            affiliate_repository=self.affiliate_repository,
            eligibility_rules=self.eligibility_rules,
            retriever=self.knowledge_retriever,
            evidence_evaluator=EvidenceEvaluator(),
        )

    @cached_property
    def analyze_coverage_use_case(self) -> AnalyzeCoverageUseCase:
        return AnalyzeCoverageUseCase(
            reasoning_engine=self.reasoning_engine,
            llm_provider=self.llm_provider,
            response_validator=ResponseValidator(),
        )

    @cached_property
    def indexing_service(self) -> IndexingService:
        return IndexingService(
            documents_path=self.settings.documents_path,
            loaders=self.document_loaders,
            normalizer=self.text_normalizer,
            chunk_strategy=self.chunk_strategy,
            embedding_provider=self.embedding_provider,
            vector_store=self.vector_store,
            index_state=self.index_state_repository,
            embedding_model=self.settings.embedding_model,
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
        )


_container: Container | None = None


def get_container() -> Container:
    """Devuelve el contenedor del proceso, creándolo si no existe."""
    global _container
    if _container is None:
        _container = Container()
    return _container


def reset_container() -> None:
    """Reinicia el contenedor (uso exclusivo en pruebas)."""
    global _container
    _container = None
