"""Normalización de texto documental (§6.6).

Limpia espacios, saltos y caracteres invisibles sin modificar jamás
el significado del texto.
"""

import re
import unicodedata

from app.domain.providers.text_normalizer import TextNormalizer

_INVISIBLE = re.compile(r"[​‌‍﻿­]")
_MULTI_SPACE = re.compile(r"[ \t]{2,}")
_MULTI_NEWLINE = re.compile(r"\n{3,}")
_TRAILING_SPACE = re.compile(r"[ \t]+$", re.MULTILINE)


class DefaultTextNormalizer(TextNormalizer):
    """Etapa de limpieza del pipeline de ingesta."""

    def normalize(self, text: str) -> str:
        text = unicodedata.normalize("NFC", text)
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = _INVISIBLE.sub("", text)
        text = _TRAILING_SPACE.sub("", text)
        text = _MULTI_SPACE.sub(" ", text)
        text = _MULTI_NEWLINE.sub("\n\n", text)
        return text.strip()
