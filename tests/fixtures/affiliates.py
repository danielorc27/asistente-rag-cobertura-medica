"""Fixtures de afiliados para pruebas."""

from datetime import date

from app.domain.entities.affiliate import Affiliate, PriorAuthorization
from app.domain.value_objects.enums import AffiliationStatus, MemberType, PaymentStatus


def make_affiliate(
    *,
    affiliate_id: str = "A-00001",
    member_type: MemberType = MemberType.HOLDER,
    plan: str = "Esencial",
    tenure_months: int = 24,
    affiliation_status: AffiliationStatus = AffiliationStatus.ACTIVE,
    payment_status: PaymentStatus = PaymentStatus.UP_TO_DATE,
    days_overdue: int = 0,
    pending_amount_cop: int = 0,
    prior_authorization: PriorAuthorization | None = None,
    declared_preexistence: bool = False,
    preexistence_description: str = "Ninguna",
    relationship: str = "N/A",
) -> Affiliate:
    """Construye un afiliado de prueba con valores por defecto razonables."""
    return Affiliate(
        affiliate_id=affiliate_id,
        document_type="CC",
        document_number="1000000000",
        first_name="Prueba",
        first_surname="Uno",
        second_surname="Dos",
        sex="F",
        birth_date=date(1990, 1, 1),
        age=36,
        city="Bogotá",
        department="Cundinamarca",
        member_type=member_type,
        relationship=relationship,
        plan=plan,
        affiliation_date=date(2024, 1, 1),
        tenure_months=tenure_months,
        affiliation_status=affiliation_status,
        payment_status=payment_status,
        days_overdue=days_overdue,
        pending_amount_cop=pending_amount_cop,
        prior_authorization=prior_authorization,
        declared_preexistence=declared_preexistence,
        preexistence_description=preexistence_description,
        contact_email="prueba@ejemplo.com",
        contact_phone="3000000000",
    )
