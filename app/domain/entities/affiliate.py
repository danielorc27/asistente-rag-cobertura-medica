"""Entidad Afiliado, alineada con el diccionario de datos de BD_afiliados."""

from dataclasses import dataclass
from datetime import date

from app.domain.value_objects.enums import AffiliationStatus, MemberType, PaymentStatus


@dataclass(frozen=True)
class PriorAuthorization:
    """Autorización previa vigente o histórica del afiliado."""

    service: str
    number: str
    issued_on: date
    valid_until: date

    def is_valid_on(self, reference: date) -> bool:
        """Indica si la autorización está vigente en la fecha dada."""
        return self.issued_on <= reference <= self.valid_until


@dataclass(frozen=True)
class Affiliate:
    """Afiliado a un plan de salud.

    Los nombres de campos siguen el diccionario de datos del archivo de
    afiliados; los datos personales se transportan pero nunca se registran
    en logs (§14.13).
    """

    affiliate_id: str
    document_type: str
    document_number: str
    first_name: str
    first_surname: str
    second_surname: str
    sex: str
    birth_date: date
    age: int
    city: str
    department: str
    member_type: MemberType
    relationship: str
    plan: str
    affiliation_date: date
    tenure_months: int
    affiliation_status: AffiliationStatus
    payment_status: PaymentStatus
    days_overdue: int
    pending_amount_cop: int
    prior_authorization: PriorAuthorization | None
    declared_preexistence: bool
    preexistence_description: str
    contact_email: str
    contact_phone: str

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.first_surname} {self.second_surname}".strip()

    @property
    def is_active(self) -> bool:
        return self.affiliation_status is AffiliationStatus.ACTIVE

    @property
    def is_in_arrears(self) -> bool:
        return self.payment_status is PaymentStatus.IN_ARREARS
