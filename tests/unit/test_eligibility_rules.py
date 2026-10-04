"""Pruebas del motor de decisión preliminar (Fase 2, §7.9/§14.6)."""

from datetime import date

import pytest
from app.domain.entities.affiliate import PriorAuthorization
from app.domain.entities.preliminary_assessment import FindingCode
from app.domain.services.eligibility_rules import EligibilityRules
from app.domain.value_objects.enums import AffiliationStatus, MemberType, PaymentStatus

from tests.fixtures.affiliates import make_affiliate

TODAY = date(2026, 6, 30)


@pytest.mark.unit
class TestEligibilityRules:
    def setup_method(self) -> None:
        self.rules = EligibilityRules()

    def _codes(self, assessment: object) -> set[FindingCode]:
        return {f.code for f in assessment.findings}  # type: ignore[attr-defined]

    def test_active_member_without_issues_is_not_blocked(self) -> None:
        assessment = self.rules.evaluate(make_affiliate(), TODAY)
        assert not assessment.blocked
        assert FindingCode.NO_PRIOR_AUTHORIZATION in self._codes(assessment)

    def test_withdrawn_member_is_blocked(self) -> None:
        affiliate = make_affiliate(affiliation_status=AffiliationStatus.WITHDRAWN)
        assessment = self.rules.evaluate(affiliate, TODAY)
        assert assessment.blocked
        assert FindingCode.AFFILIATION_NOT_ACTIVE in self._codes(assessment)

    def test_suspended_member_is_blocked(self) -> None:
        affiliate = make_affiliate(affiliation_status=AffiliationStatus.SUSPENDED)
        assert self.rules.evaluate(affiliate, TODAY).blocked

    def test_arrears_is_flagged_but_not_blocking(self) -> None:
        affiliate = make_affiliate(
            payment_status=PaymentStatus.IN_ARREARS,
            days_overdue=98,
            pending_amount_cop=240_000,
        )
        assessment = self.rules.evaluate(affiliate, TODAY)
        assert not assessment.blocked
        assert FindingCode.PAYMENTS_IN_ARREARS in self._codes(assessment)

    def test_valid_authorization_detected(self) -> None:
        auth = PriorAuthorization(
            service="Resonancia magnética de rodilla",
            number="AUT-309500",
            issued_on=date(2026, 3, 30),
            valid_until=date(2026, 7, 28),
        )
        assessment = self.rules.evaluate(make_affiliate(prior_authorization=auth), TODAY)
        assert FindingCode.AUTHORIZATION_VALID in self._codes(assessment)

    def test_expired_authorization_detected(self) -> None:
        auth = PriorAuthorization(
            service="TAC de tórax",
            number="AUT-739270",
            issued_on=date(2026, 2, 26),
            valid_until=date(2026, 4, 12),
        )
        assessment = self.rules.evaluate(make_affiliate(prior_authorization=auth), TODAY)
        assert FindingCode.AUTHORIZATION_EXPIRED in self._codes(assessment)

    def test_preexistence_and_beneficiary_flags(self) -> None:
        affiliate = make_affiliate(
            member_type=MemberType.BENEFICIARY,
            relationship="Hijo(a)",
            declared_preexistence=True,
            preexistence_description="Hipotiroidismo",
        )
        codes = self._codes(self.rules.evaluate(affiliate, TODAY))
        assert FindingCode.PREEXISTENCE_DECLARED in codes
        assert FindingCode.BENEFICIARY_MEMBER in codes
