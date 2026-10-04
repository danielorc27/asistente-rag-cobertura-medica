"""Reglas de negocio determinísticas sobre datos estructurados (§13.12, §14.4).

Solo evalúa hechos verificables del registro del afiliado. Los umbrales
que viven en los documentos (carencias, exclusiones, límites) no se
codifican aquí: los interpreta el LLM con la evidencia documental.
"""

from datetime import date

from app.domain.entities.affiliate import Affiliate
from app.domain.entities.preliminary_assessment import (
    Finding,
    FindingCode,
    PreliminaryAssessment,
)
from app.domain.value_objects.enums import MemberType


class EligibilityRules:
    """Motor de decisión preliminar (Coverage Decision Engine, §7.9)."""

    def evaluate(self, affiliate: Affiliate, reference: date) -> PreliminaryAssessment:
        """Construye la decisión preliminar a partir del registro del afiliado.

        Args:
            affiliate: registro estructurado del afiliado.
            reference: fecha de la consulta (para vigencias).

        Returns:
            PreliminaryAssessment con los hechos detectados.
        """
        findings: list[Finding] = []

        if not affiliate.is_active:
            findings.append(
                Finding(
                    code=FindingCode.AFFILIATION_NOT_ACTIVE,
                    detail=(
                        "El vínculo del afiliado no está activo "
                        f"(estado: {affiliate.affiliation_status.value})."
                    ),
                    blocking=True,
                )
            )

        if affiliate.is_in_arrears:
            findings.append(
                Finding(
                    code=FindingCode.PAYMENTS_IN_ARREARS,
                    detail=(
                        f"El afiliado presenta mora de {affiliate.days_overdue} días "
                        f"por {affiliate.pending_amount_cop} COP."
                    ),
                )
            )

        authorization = affiliate.prior_authorization
        if authorization is None:
            findings.append(
                Finding(
                    code=FindingCode.NO_PRIOR_AUTHORIZATION,
                    detail="El afiliado no cuenta con autorización previa registrada.",
                )
            )
        elif authorization.is_valid_on(reference):
            findings.append(
                Finding(
                    code=FindingCode.AUTHORIZATION_VALID,
                    detail=(
                        f"Autorización previa vigente ({authorization.number}) para "
                        f"'{authorization.service}' hasta {authorization.valid_until.isoformat()}."
                    ),
                )
            )
        else:
            findings.append(
                Finding(
                    code=FindingCode.AUTHORIZATION_EXPIRED,
                    detail=(
                        f"La autorización {authorization.number} para "
                        f"'{authorization.service}' venció el "
                        f"{authorization.valid_until.isoformat()}."
                    ),
                )
            )

        if affiliate.declared_preexistence:
            findings.append(
                Finding(
                    code=FindingCode.PREEXISTENCE_DECLARED,
                    detail=(
                        f"El afiliado declaró preexistencia: {affiliate.preexistence_description}."
                    ),
                )
            )

        if affiliate.member_type is MemberType.BENEFICIARY:
            findings.append(
                Finding(
                    code=FindingCode.BENEFICIARY_MEMBER,
                    detail=f"El afiliado es beneficiario (parentesco: {affiliate.relationship}).",
                )
            )

        return PreliminaryAssessment(findings=tuple(findings))
