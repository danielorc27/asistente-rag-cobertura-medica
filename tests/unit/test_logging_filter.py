"""Pruebas del filtro de datos sensibles en logs (§14.13)."""

import logging

import pytest
from app.config.logging import SensitiveDataFilter


def _record(message: str) -> logging.LogRecord:
    return logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg=message,
        args=(),
        exc_info=None,
    )


@pytest.mark.unit
class TestSensitiveDataFilter:
    def test_redacts_document_number(self) -> None:
        record = _record("consulta afiliado numero_documento=1023456789")
        SensitiveDataFilter().filter(record)
        assert "1023456789" not in record.getMessage()
        assert "***" in record.getMessage()

    def test_redacts_names_and_contact(self) -> None:
        record = _record("primer_nombre: 'Miguel' correo_contacto=a@b.co")
        SensitiveDataFilter().filter(record)
        message = record.getMessage()
        assert "Miguel" not in message
        assert "a@b.co" not in message

    def test_keeps_non_sensitive_message(self) -> None:
        record = _record("indexados 348 chunks en 18.4 s")
        SensitiveDataFilter().filter(record)
        assert record.getMessage() == "indexados 348 chunks en 18.4 s"
