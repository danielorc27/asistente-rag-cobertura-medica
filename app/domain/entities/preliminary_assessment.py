"""Decisión preliminar del Coverage Decision Engine (§7.9, §14.6).

Se construye únicamente con datos estructurados del afiliado.
La interpretación de las reglas documentales corresponde al LLM
con la evidencia recuperada.
"""

from dataclasses import dataclass, field
from enum import StrEnum


class FindingCode(StrEnum):
    """Hechos estructurados detectados sobre el afiliado."""

    AFFILIATION_NOT_ACTIVE = "AFFILIATION_NOT_ACTIVE"
    PAYMENTS_IN_ARREARS = "PAYMENTS_IN_ARREARS"
    AUTHORIZATION_VALID = "AUTHORIZATION_VALID"
    AUTHORIZATION_EXPIRED = "AUTHORIZATION_EXPIRED"
    NO_PRIOR_AUTHORIZATION = "NO_PRIOR_AUTHORIZATION"
    PREEXISTENCE_DECLARED = "PREEXISTENCE_DECLARED"
    BENEFICIARY_MEMBER = "BENEFICIARY_MEMBER"


@dataclass(frozen=True)
class Finding:
    """Hecho verificable derivado de los datos del afiliado.

    ``blocking`` marca condiciones que impiden la cobertura de plano
    (p. ej. vínculo no activo); el resto son insumos para el análisis
    documental.
    """

    code: FindingCode
    detail: str
    blocking: bool = False


@dataclass(frozen=True)
class PreliminaryAssessment:
    """Resultado del análisis determinístico previo al LLM."""

    findings: tuple[Finding, ...] = field(default=())

    @property
    def blocked(self) -> bool:
        return any(f.blocking for f in self.findings)

    @property
    def blocking_findings(self) -> tuple[Finding, ...]:
        return tuple(f for f in self.findings if f.blocking)
