"""Controller de administración y diagnóstico (§9.13, §14.8)."""

from app.application.services.indexing_service import IndexingService
from app.domain.providers.vector_store import VectorStore
from app.domain.repositories.affiliate_repository import AffiliateRepository
from app.presentation.schemas.admin import HealthResponse, ReindexRequest, ReindexResponse


class AdminController:
    def __init__(
        self,
        indexing_service: IndexingService,
        vector_store: VectorStore,
        affiliate_repository: AffiliateRepository,
        llm_configured: bool,
        version: str,
    ) -> None:
        self._indexing_service = indexing_service
        self._vector_store = vector_store
        self._affiliate_repository = affiliate_repository
        self._llm_configured = llm_configured
        self._version = version

    def reindex(self, request: ReindexRequest) -> ReindexResponse:
        report = self._indexing_service.run(request.mode)
        return ReindexResponse.from_application(report)

    def health(self) -> HealthResponse:
        vector_ok, chunks = self._probe_vector_store()
        affiliates_ok = self._probe_affiliates()
        index_ready = vector_ok and self._indexing_service.is_index_ready()
        healthy = vector_ok and affiliates_ok and self._llm_configured
        return HealthResponse(
            status="ok" if healthy else "degraded",
            version=self._version,
            vector_store_available=vector_ok,
            indexed_chunks=chunks,
            index_ready=index_ready,
            affiliate_repository_available=affiliates_ok,
            llm_configured=self._llm_configured,
        )

    def _probe_vector_store(self) -> tuple[bool, int]:
        try:
            return True, self._vector_store.count()
        except Exception:  # diagnóstico: cualquier fallo = no disponible
            return False, 0

    def _probe_affiliates(self) -> bool:
        try:
            # Sonda liviana: una búsqueda inexistente valida acceso a la fuente.
            self._affiliate_repository.find_by_id("__health_check__")
            return True
        except Exception:
            return False
