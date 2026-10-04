"""Punto de entrada de la aplicación.

Secuencia de arranque (§9.7): configuración → logging → dependencias →
verificación del índice → registro de rutas → API lista.
"""

import logging

from fastapi import FastAPI

from app.config.dependencies import Container, get_container
from app.config.logging import configure_logging
from app.presentation.controllers.admin_controller import AdminController
from app.presentation.controllers.coverage_controller import CoverageController
from app.presentation.middleware.error_handlers import register_error_handlers
from app.presentation.middleware.metrics_middleware import register_metrics_middleware
from app.presentation.routers.api_router import router
from app.shared.metrics import MetricsCollector

logger = logging.getLogger(__name__)

APP_VERSION = "0.1.0"


def create_app(container: Container | None = None) -> FastAPI:
    """Crea y configura la aplicación FastAPI.

    ``container`` permite inyectar dependencias simuladas en pruebas.
    """
    container = container or get_container()
    settings = container.settings
    configure_logging(settings.log_level, settings.log_file)
    logger.info("Configuración cargada. Iniciando aplicación (debug=%s).", settings.debug)

    app = FastAPI(
        title="Asistente de Validación de Cobertura",
        description="Valida cobertura de procedimientos médicos mediante RAG.",
        version=APP_VERSION,
    )

    # Estado compartido de la capa de presentación (§14.3: cableado en el
    # composition root; los routers solo consumen).
    app.state.metrics = MetricsCollector()
    app.state.reindex_api_key = settings.reindex_api_key
    app.state.coverage_controller = CoverageController(use_case=container.analyze_coverage_use_case)
    app.state.admin_controller = AdminController(
        indexing_service=container.indexing_service,
        vector_store=container.vector_store,
        affiliate_repository=container.affiliate_repository,
        llm_configured=bool(settings.openai_api_key) or settings.llm_provider == "mock",
        version=APP_VERSION,
    )

    register_metrics_middleware(app)
    register_error_handlers(app)
    app.include_router(router)

    _verify_index(container)
    logger.info("Aplicación inicializada.")
    return app


def _verify_index(container: Container) -> None:
    """Verificación del índice al arranque (§9.8); nunca reindexa sola (§9.9)."""
    try:
        if container.indexing_service.is_index_ready():
            logger.info("Índice vectorial disponible y compatible.")
        else:
            logger.warning(
                "Índice vectorial ausente o incompatible. Ejecute "
                "'python scripts/index_documents.py' o POST /reindex."
            )
    except Exception as exc:  # el arranque no debe caer por el diagnóstico
        logger.error("No fue posible verificar el índice: %s", exc)


app = create_app()
