"""Contrato de acceso a datos de afiliados (§3.3)."""

from abc import ABC, abstractmethod

from app.domain.entities.affiliate import Affiliate


class AffiliateRepository(ABC):
    """Puerto de consulta de afiliados; oculta por completo el origen de datos."""

    @abstractmethod
    def find_by_id(self, affiliate_id: str) -> Affiliate | None:
        """Busca un afiliado por su identificador único (formato A-#####).

        Returns:
            El afiliado, o ``None`` si no existe.
        """
