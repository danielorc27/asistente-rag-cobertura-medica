"""Repositorio de afiliados sobre Excel (§3.3, §5.10).

Único módulo del proyecto autorizado a usar Pandas. Carga la hoja
'Afiliados' una sola vez y mapea cada fila a la entidad del dominio con
validación explícita: un valor inesperado produce AffiliateDataError,
nunca corrupción silenciosa.
"""

import logging
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from app.domain.entities.affiliate import Affiliate, PriorAuthorization
from app.domain.exceptions.errors import AffiliateDataError, ConfigurationError
from app.domain.repositories.affiliate_repository import AffiliateRepository
from app.domain.value_objects.enums import AffiliationStatus, MemberType, PaymentStatus

logger = logging.getLogger(__name__)

_SHEET_NAME = "Afiliados"
_YES = "sí"


class ExcelAffiliateRepository(AffiliateRepository):
    """Implementación de AffiliateRepository sobre BD_afiliados.xlsx."""

    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path
        self._frame: pd.DataFrame | None = None

    def find_by_id(self, affiliate_id: str) -> Affiliate | None:
        frame = self._load()
        rows = frame[frame["id_afiliado"] == affiliate_id.strip()]
        if rows.empty:
            return None
        return self._map_row(rows.iloc[0])

    def _load(self) -> pd.DataFrame:
        if self._frame is None:
            if not self._file_path.exists():
                raise ConfigurationError(f"Archivo de afiliados no encontrado: {self._file_path}")
            try:
                self._frame = pd.read_excel(self._file_path, sheet_name=_SHEET_NAME)
            except ValueError as exc:
                raise ConfigurationError(
                    f"El archivo de afiliados no contiene la hoja '{_SHEET_NAME}'."
                ) from exc
            logger.info("Repositorio de afiliados cargado: %d registros.", len(self._frame))
        return self._frame

    def _map_row(self, row: "pd.Series[Any]") -> Affiliate:
        affiliate_id = str(row["id_afiliado"])
        try:
            return Affiliate(
                affiliate_id=affiliate_id,
                document_type=self._text(row, "tipo_documento"),
                document_number=self._text(row, "numero_documento"),
                first_name=self._text(row, "primer_nombre"),
                first_surname=self._text(row, "primer_apellido"),
                second_surname=self._text(row, "segundo_apellido"),
                sex=self._text(row, "sexo"),
                birth_date=self._date(row, "fecha_nacimiento"),
                age=int(row["edad"]),
                city=self._text(row, "ciudad"),
                department=self._text(row, "departamento"),
                member_type=MemberType(self._text(row, "tipo_afiliado")),
                relationship=self._text(row, "parentesco"),
                plan=self._text(row, "plan"),
                affiliation_date=self._date(row, "fecha_afiliacion"),
                tenure_months=int(row["antiguedad_meses"]),
                affiliation_status=AffiliationStatus(self._text(row, "estado_afiliacion")),
                payment_status=PaymentStatus(self._text(row, "estado_pagos")),
                days_overdue=int(row["dias_mora"]),
                pending_amount_cop=int(row["valor_pendiente_cop"]),
                prior_authorization=self._authorization(row),
                declared_preexistence=self._yes_no(row, "preexistencia_declarada"),
                preexistence_description=self._text(row, "descripcion_preexistencia"),
                contact_email=self._text(row, "correo_contacto"),
                contact_phone=self._text(row, "telefono_contacto"),
            )
        except (KeyError, ValueError, TypeError) as exc:
            raise AffiliateDataError(
                f"Registro inválido para el afiliado {affiliate_id}: {exc}"
            ) from exc

    def _authorization(self, row: "pd.Series[Any]") -> PriorAuthorization | None:
        if not self._yes_no(row, "tiene_autorizacion_previa"):
            return None
        number = self._text(row, "numero_autorizacion")
        if not number:
            raise ValueError("tiene_autorizacion_previa='Sí' sin numero_autorizacion")
        return PriorAuthorization(
            service=self._text(row, "servicio_autorizado"),
            number=number,
            issued_on=self._date(row, "fecha_autorizacion"),
            valid_until=self._date(row, "vigencia_autorizacion"),
        )

    @staticmethod
    def _text(row: "pd.Series[Any]", column: str) -> str:
        value = row[column]
        if pd.isna(value):
            return ""
        return str(value).strip()

    @staticmethod
    def _date(row: "pd.Series[Any]", column: str) -> date:
        value = row[column]
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str) and value.strip():
            return date.fromisoformat(value.strip())
        raise ValueError(f"Fecha inválida en columna '{column}': {value!r}")

    def _yes_no(self, row: "pd.Series[Any]", column: str) -> bool:
        value = self._text(row, column).lower()
        if value in (_YES, "si"):
            return True
        if value == "no":
            return False
        raise ValueError(f"Valor Sí/No inválido en columna '{column}': {value!r}")
