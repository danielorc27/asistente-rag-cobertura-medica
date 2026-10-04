"""Value objects enumerados del dominio."""

from enum import StrEnum


class CoverageStatus(StrEnum):
    """Estado final de una decisión de cobertura (§7.9)."""

    APPROVED = "APPROVED"
    APPROVED_WITH_RESTRICTIONS = "APPROVED_WITH_RESTRICTIONS"
    REJECTED = "REJECTED"
    INSUFFICIENT_INFORMATION = "INSUFFICIENT_INFORMATION"


class EvidenceStrength(StrEnum):
    """Fuerza de la evidencia documental recuperada (§14.7).

    Sustituye al porcentaje de confianza; se deriva de reglas explícitas
    sobre los scores de retrieval, nunca lo inventa el LLM.
    """

    INSUFFICIENT = "INSUFFICIENT"
    PARTIAL = "PARTIAL"
    STRONG = "STRONG"


class AffiliationStatus(StrEnum):
    """Estado del vínculo del afiliado, según BD_afiliados."""

    ACTIVE = "Activo"
    SUSPENDED = "Suspendido"
    WITHDRAWN = "Retirado"


class PaymentStatus(StrEnum):
    """Estado de pagos del afiliado, según BD_afiliados."""

    UP_TO_DATE = "Al día"
    IN_ARREARS = "En mora"


class MemberType(StrEnum):
    """Rol del afiliado dentro del plan."""

    HOLDER = "Titular"
    BENEFICIARY = "Beneficiario"
