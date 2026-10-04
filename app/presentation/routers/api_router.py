"""Registro de endpoints (§4.5) y seguridad del reindex (§14.8)."""

import secrets
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import FileResponse

from app.presentation.controllers.admin_controller import AdminController
from app.presentation.controllers.coverage_controller import CoverageController
from app.presentation.schemas.admin import HealthResponse, ReindexRequest, ReindexResponse
from app.presentation.schemas.coverage import QueryRequest, QueryResponse

router = APIRouter()

_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@router.get("/", include_in_schema=False)
def get_ui() -> FileResponse:
    """Interfaz web mínima para probar consultas (sin dependencias externas)."""
    return FileResponse(_STATIC_DIR / "index.html", media_type="text/html")


def _coverage_controller(request: Request) -> CoverageController:
    controller: CoverageController = request.app.state.coverage_controller
    return controller


def _admin_controller(request: Request) -> AdminController:
    controller: AdminController = request.app.state.admin_controller
    return controller


def _require_reindex_key(
    request: Request,
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> None:
    """Protección de POST /reindex mediante API Key configurable (§14.8)."""
    configured: str = request.app.state.reindex_api_key
    if not configured:
        raise HTTPException(
            status_code=503,
            detail="Reindexación deshabilitada: REINDEX_API_KEY no está configurada.",
        )
    if x_api_key is None or not secrets.compare_digest(x_api_key, configured):
        raise HTTPException(status_code=401, detail="API Key inválida o ausente.")


@router.post("/query", response_model=QueryResponse, tags=["coverage"])
def post_query(
    body: QueryRequest,
    controller: Annotated[CoverageController, Depends(_coverage_controller)],
) -> QueryResponse:
    """Analiza si un procedimiento está cubierto por el plan del afiliado."""
    return controller.query(body)


@router.post(
    "/reindex",
    response_model=ReindexResponse,
    tags=["admin"],
    dependencies=[Depends(_require_reindex_key)],
)
def post_reindex(
    body: ReindexRequest,
    controller: Annotated[AdminController, Depends(_admin_controller)],
) -> ReindexResponse:
    """Reconstruye o actualiza el índice vectorial (§6.14)."""
    return controller.reindex(body)


@router.get("/health", response_model=HealthResponse, tags=["admin"])
def get_health(
    controller: Annotated[AdminController, Depends(_admin_controller)],
) -> HealthResponse:
    """Diagnóstico del servicio y sus dependencias (§9.13)."""
    return controller.health()


@router.get("/metrics", tags=["admin"])
def get_metrics(request: Request) -> dict[str, object]:
    """Métricas de operación en memoria (§9.14)."""
    snapshot: dict[str, object] = request.app.state.metrics.snapshot()
    return snapshot
