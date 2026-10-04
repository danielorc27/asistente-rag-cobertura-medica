"""Configuración global de logging (§9.10, §14.13).

Incluye un filtro que impide registrar datos sensibles del afiliado:
nombres, número de documento, contactos y descripciones médicas.
"""

import logging
import logging.config
import re
from pathlib import Path

# Campos que nunca deben aparecer en logs (§14.13). Se redactan si un
# mensaje incluye pares clave=valor o "clave": valor con estos nombres.
_SENSITIVE_FIELDS = (
    "primer_nombre",
    "primer_apellido",
    "segundo_apellido",
    "numero_documento",
    "correo_contacto",
    "telefono_contacto",
    "descripcion_preexistencia",
    "api_key",
    "authorization",
)

_SENSITIVE_PATTERN = re.compile(
    r"(?P<key>\b(?:"
    + "|".join(_SENSITIVE_FIELDS)
    + r")\b\s*[=:]\s*)(?P<value>'[^']*'|\"[^\"]*\"|\S+)",
    flags=re.IGNORECASE,
)


class SensitiveDataFilter(logging.Filter):
    """Redacta valores de campos sensibles antes de emitir el registro."""

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        redacted = _SENSITIVE_PATTERN.sub(r"\g<key>***", message)
        if redacted != message:
            record.msg = redacted
            record.args = ()
        return True


def configure_logging(level: str, log_file: Path) -> None:
    """Configura logging para consola y archivo con filtro de datos sensibles."""
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {"sensitive": {"()": SensitiveDataFilter}},
            "formatters": {
                "standard": {
                    "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "filters": ["sensitive"],
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": str(log_file),
                    "maxBytes": 5_000_000,
                    "backupCount": 3,
                    "encoding": "utf-8",
                    "formatter": "standard",
                    "filters": ["sensitive"],
                },
            },
            "root": {"level": level.upper(), "handlers": ["console", "file"]},
        }
    )
