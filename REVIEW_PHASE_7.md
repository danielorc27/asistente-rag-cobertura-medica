# Revisión de Fase 7 — Testing Consolidado

**Fecha:** 2026-07-17
**Estado:** COMPLETADA — 110/110 pruebas, cobertura global 96%, Ruff limpio, MyPy strict sin errores.

---

## 1. Suite consolidada

| Nivel | Cantidad | Contenido |
|---|---|---|
| Unit | 63 | Dominio (reglas, entidades, VOs, pureza AST), configuración, logging, chunking, normalización, providers con fakes, factories, retriever, evaluador, prompt builder, response validator, use case, métricas |
| Integration | 33 | Loader Word vs docs reales (incl. tablas), Excel repo vs archivo real, Chroma persistente, manifiesto, pipeline de ingesta completo con 3 modos |
| E2E | 14 | API completa: happy path, 404/422/502, seguridad de reindex, health, métricas, casos límite |
| **Total** | **110** | |

### Casos límite cubiertos (§11.15)
- Afiliado inexistente → 404 ✔
- Documento vacío / corrupto / sin loader → ingesta continúa ✔
- Documento actualizado / duplicado (hash) ✔
- Vector store vacío → INSUFFICIENT_INFORMATION sin invocar LLM ✔
- Proveedor LLM caído → 502 tipificado ✔
- Consulta muy larga (9.000 chars) → sin error 500 ✔
- Consulta ambigua / fuera de dominio → respuesta honesta ✔
- Consulta sin afiliado → 422 ✔
- App sin API Key → arranca, health `degraded` ✔

## 2. Golden set de evaluación (§8.19, §11.19)

- `tests/fixtures/golden_set.json`: 10 casos diseñados sobre afiliados reales del Excel (autorización vencida, retirado en mora, beneficiario, exclusiones estéticas, pregunta fuera de dominio, copagos en tablas, afiliado inexistente). Cada caso declara status aceptables, expectativa de evidencia y justificación.
- `scripts/evaluate_golden_set.py`: lo ejecuta contra el sistema **real** (LLM + índice reales) y reporta PASS/FAIL por caso. Es la herramienta de regresión para cambios de prompt (§8.19) y produce la evidencia objetiva de calidad (§11.19).

**Pendiente de ejecución real:** requiere `OPENAI_API_KEY`. Los 110 tests automatizados corren 100% offline.

## 3. Métricas de calidad (§10.21, §11.17)

- Cobertura: **96%** (objetivo ≥80%). Módulos de negocio (domain/application) ≥96%.
- MyPy strict: 0 errores en 81 archivos. Ruff: 0 advertencias.
- Suite completa: ~35 s (unit sola: <3 s).

## 4. Problemas encontrados

- Ninguno nuevo; los casos límite pasaron con el diseño existente sin cambios de código productivo (validación de que la arquitectura maneja degradación por diseño, §13.14).

## 5. Riesgos

1. La calidad del razonamiento con el LLM real solo se medirá al ejecutar el golden set con API Key — los stubs validan contrato y guardrails, no la calidad de redacción.
2. `test_very_long_question_is_handled` acepta 200 o 502: con modelos reales, una consulta de 9.000 caracteres puede exceder límites del proveedor; el contrato exige solo error controlado.

## 6. Validación contra ESPECIFICACION.md

- Pirámide de pruebas (§11.3): 63 unit > 33 integration > 14 e2e ✔
- Sin OpenAI/Chroma reales en unit (§11.4) ✔ (Chroma real solo en sus pruebas de integración con tmp_path)
- Escenarios de ingesta (§11.7), chunking (§11.8), vector store (§11.9), retrieval (§11.10), razonamiento (§11.11), prompts (§11.12), LLM (§11.13), guardrails (§11.14) ✔
- Evidencia de calidad (§11.19): reporte de cobertura + golden set + logs ✔

**Conclusión:** Fase 7 cumple la Definition of Done. Las Fases 8 (optimización) y 9 (documentación) pueden ejecutarse sobre una base verificada.
