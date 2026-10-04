# Revisión de Fase 2 — Dominio

**Fecha:** 2026-07-17
**Estado:** COMPLETADA — 20/20 pruebas, Ruff limpio, MyPy strict sin errores.

---

## 1. Componentes implementados

### Entidades (`app/domain/entities/`)
| Componente | Descripción |
|---|---|
| `Affiliate` | Afiliado con los 29 campos del diccionario de datos real de `BD_afiliados.xlsx`, tipado fuerte (`date`, enums). Propiedades: `full_name`, `is_active`, `is_in_arrears`. |
| `PriorAuthorization` | Value object anidado con `is_valid_on(fecha)` para vigencia de autorizaciones. |
| `Document` | Modelo uniforme que entrega cualquier `DocumentLoader` (§3.4): id, nombre, fuente, tipo, tamaño, fecha, contenido, hash. |
| `PreliminaryAssessment` + `Finding` + `FindingCode` | Decisión preliminar del Coverage Decision Engine (§7.9): hechos estructurados con marca `blocking`. |

### Value objects (`app/domain/value_objects/`)
- `CoverageStatus` (APPROVED / APPROVED_WITH_RESTRICTIONS / REJECTED / INSUFFICIENT_INFORMATION).
- `EvidenceStrength` (INSUFFICIENT / PARTIAL / STRONG) — sustituye al confidence numérico (§14.7).
- `AffiliationStatus`, `PaymentStatus`, `MemberType` — mapean los valores reales del Excel.
- `DocumentChunk` — fragmento inmutable con trazabilidad completa (§6.10) y `similarity` opcional.

### Servicios de dominio (`app/domain/services/`)
- `EligibilityRules` (§14.4): reglas determinísticas sobre datos estructurados. Detecta: vínculo no activo (bloqueante), mora, autorización vigente/vencida/ausente, preexistencia declarada, condición de beneficiario.

### Contratos / Ports
- `AffiliateRepository` (§3.3): `find_by_id() -> Affiliate | None`.
- `IndexStateRepository` + `IndexManifest` (§14.11): manifiesto del índice con verificación de compatibilidad de parámetros.
- `LLMProvider` + `LLMRequest`/`LLMResult` (§3.8): una llamada, salida JSON, metadatos de trazabilidad (modelo, tokens, latencia).
- `EmbeddingProvider` (§3.6): batching de listas permitido (§14.12).
- `VectorStore` + `VectorRecord` (§3.7): upsert, search con similarity, `delete_document` (§14.11), count.
- `DocumentLoader` (§3.4): `supports()` + `load()`, modelo uniforme.
- `ChunkStrategy` (§3.5): `split(text) -> list[str]`.

### Excepciones (`app/domain/exceptions/`)
Jerarquía con base `DomainError`: `ConfigurationError`, `AffiliateNotFoundError`, `DocumentLoadError`, `IndexInvalidError`, `LLMProviderError`, `EmbeddingProviderError`, `ResponseValidationError` — alineada con las categorías de §9.11.

---

## 2. Decisiones tomadas

1. **`plan` es `str`, no enum.** Los nombres de planes (Esencial/Clásico/Premium) son datos de negocio definidos en DOC1; codificarlos como enum sería hardcodear contenido documental (§7-Restricciones). Los estados (`Activo`, `En mora`...) sí son enums porque son dominios cerrados del diccionario de datos.
2. **Los umbrales de carencia NO se codifican.** `antiguedad_meses` viaja en la entidad, pero los meses requeridos por procedimiento viven en DOC2 y los interpretará el LLM con evidencia (§14.6). Codificarlos duplicaría la fuente de verdad documental (§13.2).
3. **`Finding.blocking` solo para vínculo no activo.** La mora NO bloquea de plano: sus consecuencias las definen los documentos (DOC2), así que se reporta como hecho no bloqueante para que el razonamiento documental decida.
4. **Autorización previa como value object opcional** (`PriorAuthorization | None`) en lugar de 5 columnas sueltas: los campos del Excel (`numero_autorizacion`, `fecha_autorizacion`, `vigencia_autorizacion`) solo tienen sentido juntos.
5. **Dataclasses frozen en todo el dominio**: inmutabilidad garantiza que ninguna capa modifique datos del afiliado (guardrail §8.9) y facilita testing.
6. **`LLMResult` transporta tokens y latencia** para satisfacer trazabilidad (§7.18) y métricas (§9.14) sin acoplar el dominio al SDK.
7. **Prueba de pureza arquitectónica por AST** (`test_domain_purity.py`): verifica ejecutablemente que `app/domain` solo importa stdlib y a sí mismo — es la Regla de Oro (§2.13) convertida en test, complementando las reglas `banned-api` de Ruff.

## 3. Cobertura de pruebas

20 pruebas (todas `@pytest.mark.unit`), en `tests/unit/` + fixture builder `tests/fixtures/affiliates.py`.

| Área | Cobertura |
|---|---|
| `entities/affiliate.py` | 100% |
| `entities/document.py` | 100% |
| `entities/preliminary_assessment.py` | 96% |
| `services/eligibility_rules.py` | 100% |
| `value_objects/*` | 100% |
| `repositories/index_state_repository.py` | 100% |
| Ports abstractos (`providers/*`, `affiliate_repository`) y excepciones | 0% — esperado: son contratos sin lógica; se ejercitan cuando existan implementaciones (Fases 3–5) |

Toda la lógica ejecutable del dominio está en 96–100%.

## 4. Problemas encontrados

- Faltaba `tests/fixtures/__init__.py`, lo que rompía los imports de fixtures; corregido.
- Ningún otro problema: MyPy strict y Ruff pasan sin excepciones ni `type: ignore` en código productivo (hay un único `type: ignore[attr-defined]` en un helper de test).

## 5. Riesgos

1. **Mapeo Excel → entidad (Fase 3):** los valores con tilde ("Al día", "Sí") y fechas ISO del Excel deben mapearse con cuidado a los enums; un valor inesperado debe producir error claro, no corrupción silenciosa. Mitigación prevista: validación explícita en `ExcelAffiliateRepository` con pruebas sobre el archivo real.
2. **`blocking` conservador:** solo el vínculo no activo bloquea. Si DOC2 define otras condiciones de rechazo automático (p. ej. mora > N días suspende el servicio), la decisión final dependerá de que el retrieval recupere esa regla. Riesgo aceptado y coherente con §13.2 (la fuente de verdad son los documentos).
3. **`FindingCode` es extensible pero cerrado:** nuevas reglas estructuradas requieren tocar el enum del dominio. Aceptable: son cambios de negocio, no de tecnología (§2.10 protege contra cambios tecnológicos, no de dominio).

## 6. Validación contra ESPECIFICACION.md

| Regla | Cumplimiento |
|---|---|
| Dominio sin librerías externas (§2.4, §5.17) | ✔ garantizado por test AST + Ruff banned-api |
| Dependencias apuntan al dominio (§14.1) | ✔ el dominio no importa ninguna otra capa |
| Interfaces en `domain/repositories` y `domain/providers` (§14.3) | ✔ sin `application/interfaces/` |
| Reglas determinísticas en Domain (§14.4) | ✔ `EligibilityRules` |
| EvidenceStrength en lugar de confidence (§14.7) | ✔ enum de 3 niveles |
| Decisión preliminar solo con datos estructurados (§14.6) | ✔ `EligibilityRules` no toca documentos |
| Tipado completo (§10.9) | ✔ MyPy strict sin errores |
| Convenciones de nombres (§4.12) | ✔ PascalCase/snake_case, sufijos Repository/Provider/Strategy |
| Sin hardcodeo de nombres de documentos/modelos (§7) | ✔ |
| Manifiesto del índice (§14.11) | ✔ contrato `IndexStateRepository` + `IndexManifest` |
| Pruebas por fase (§14.9) | ✔ 20 pruebas unitarias entregadas con la fase |

**Conclusión:** la Fase 2 cumple la Definition of Done (§12.14). El dominio queda estable como base para implementar los adapters de la Fase 3.
