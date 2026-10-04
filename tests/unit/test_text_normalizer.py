"""Pruebas del normalizador de texto (Fase 3, §6.6)."""

import pytest
from app.infrastructure.parser.text_normalizer import DefaultTextNormalizer


@pytest.mark.unit
class TestTextNormalizer:
    def setup_method(self) -> None:
        self.normalizer = DefaultTextNormalizer()

    def test_collapses_spaces_and_newlines(self) -> None:
        text = "Cobertura   del  plan\n\n\n\nPremium\t\tincluye."
        result = self.normalizer.normalize(text)
        assert "   " not in result
        assert "\n\n\n" not in result

    def test_preserves_meaning(self) -> None:
        text = "El copago será del 20% para el plan Clásico."
        assert self.normalizer.normalize(text) == text

    def test_normalizes_line_endings(self) -> None:
        assert self.normalizer.normalize("a\r\nb\rc") == "a\nb\nc"

    def test_strips_invisible_characters(self) -> None:
        assert self.normalizer.normalize("plan​Premium") == "planPremium"
