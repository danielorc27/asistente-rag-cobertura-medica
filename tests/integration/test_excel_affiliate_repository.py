"""Pruebas de integración del repositorio de afiliados contra el Excel real."""

from datetime import date
from pathlib import Path

import pytest
from app.domain.exceptions.errors import ConfigurationError
from app.domain.value_objects.enums import AffiliationStatus, MemberType, PaymentStatus
from app.infrastructure.repositories.excel_affiliate_repository import ExcelAffiliateRepository

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "BD_afiliados.xlsx"


@pytest.mark.integration
class TestExcelAffiliateRepository:
    def setup_method(self) -> None:
        self.repository = ExcelAffiliateRepository(file_path=DATA_FILE)

    def test_finds_existing_affiliate_with_authorization(self) -> None:
        affiliate = self.repository.find_by_id("A-00001")
        assert affiliate is not None
        assert affiliate.member_type is MemberType.HOLDER
        assert affiliate.plan == "Esencial"
        assert affiliate.affiliation_status is AffiliationStatus.ACTIVE
        assert affiliate.payment_status is PaymentStatus.UP_TO_DATE
        assert affiliate.prior_authorization is not None
        assert affiliate.prior_authorization.number == "AUT-309500"
        assert affiliate.prior_authorization.valid_until == date(2026, 6, 28)
        assert affiliate.declared_preexistence

    def test_finds_affiliate_without_authorization(self) -> None:
        affiliate = self.repository.find_by_id("A-00002")
        assert affiliate is not None
        assert affiliate.prior_authorization is None
        assert not affiliate.declared_preexistence

    def test_withdrawn_affiliate_in_arrears(self) -> None:
        affiliate = self.repository.find_by_id("A-00003")
        assert affiliate is not None
        assert affiliate.affiliation_status is AffiliationStatus.WITHDRAWN
        assert affiliate.is_in_arrears
        assert affiliate.days_overdue == 98
        assert affiliate.pending_amount_cop == 240_000

    def test_unknown_affiliate_returns_none(self) -> None:
        assert self.repository.find_by_id("A-99999") is None

    def test_id_is_trimmed(self) -> None:
        assert self.repository.find_by_id("  A-00001 ") is not None

    def test_missing_file_raises_configuration_error(self) -> None:
        repository = ExcelAffiliateRepository(file_path=Path("no/existe.xlsx"))
        with pytest.raises(ConfigurationError):
            repository.find_by_id("A-00001")
