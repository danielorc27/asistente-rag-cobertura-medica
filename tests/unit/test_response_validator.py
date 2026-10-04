"""Pruebas del Response Validator (Fase 5, §7.12, §11.14)."""

import json

import pytest
from app.application.reasoning.response_validator import ResponseValidator
from app.domain.exceptions.errors import ResponseValidationError
from app.domain.value_objects.enums import CoverageStatus

ALLOWED = {"c1", "c2"}


def _payload(**overrides: object) -> str:
    base: dict[str, object] = {
        "status": "APPROVED",
        "summary": "La solicitud procede.",
        "reasoning": "El procedimiento está cubierto para este plan.",
        "citations": ["c1"],
        "warnings": [],
    }
    base.update(overrides)
    return json.dumps(base)


@pytest.mark.unit
class TestResponseValidator:
    def setup_method(self) -> None:
        self.validator = ResponseValidator()

    def test_valid_response_is_parsed(self) -> None:
        parsed = self.validator.validate(_payload(), ALLOWED)
        assert parsed.status is CoverageStatus.APPROVED
        assert parsed.citations == ("c1",)

    def test_invalid_json_rejected(self) -> None:
        with pytest.raises(ResponseValidationError, match="JSON"):
            self.validator.validate("no es json {", ALLOWED)

    def test_missing_fields_rejected(self) -> None:
        with pytest.raises(ResponseValidationError, match="Faltan campos"):
            self.validator.validate(json.dumps({"status": "APPROVED"}), ALLOWED)

    def test_invalid_status_rejected(self) -> None:
        with pytest.raises(ResponseValidationError, match="Status inválido"):
            self.validator.validate(_payload(status="TAL_VEZ"), ALLOWED)

    def test_hallucinated_citation_rejected(self) -> None:
        """Citar un chunk no suministrado es alucinación detectable (§7.14)."""
        with pytest.raises(ResponseValidationError, match="no suministrados"):
            self.validator.validate(_payload(citations=["c1", "inventado"]), ALLOWED)

    def test_decision_without_citations_rejected(self) -> None:
        with pytest.raises(ResponseValidationError, match="al menos una cita"):
            self.validator.validate(_payload(citations=[]), ALLOWED)

    def test_insufficient_information_allows_no_citations(self) -> None:
        parsed = self.validator.validate(
            _payload(status="INSUFFICIENT_INFORMATION", citations=[]), ALLOWED
        )
        assert parsed.status is CoverageStatus.INSUFFICIENT_INFORMATION

    def test_empty_summary_rejected(self) -> None:
        with pytest.raises(ResponseValidationError, match="vacíos"):
            self.validator.validate(_payload(summary="  "), ALLOWED)
