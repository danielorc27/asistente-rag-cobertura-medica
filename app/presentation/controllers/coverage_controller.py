"""Controller de consultas de cobertura (§2.8).

Recibe el request, invoca el caso de uso y convierte la respuesta.
Cero lógica de negocio.
"""

from app.application.use_cases.analyze_coverage_use_case import AnalyzeCoverageUseCase
from app.presentation.schemas.coverage import QueryRequest, QueryResponse


class CoverageController:
    def __init__(self, use_case: AnalyzeCoverageUseCase) -> None:
        self._use_case = use_case

    def query(self, request: QueryRequest) -> QueryResponse:
        response = self._use_case.execute(request.to_application())
        return QueryResponse.from_application(response)
