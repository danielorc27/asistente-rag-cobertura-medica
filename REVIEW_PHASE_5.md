# Revisión de Fase 5 — Pipeline de Consulta y Motor de Razonamiento

**Fecha:** 2026-07-17
**Estado:** COMPLETADA — 93/93 pruebas, Ruff limpio, MyPy strict sin errores, cobertura de Application 96%.

---

## 1. Componentes implementados

| Componente | Módulo | Rol (§7.4) |
|---|---|---|
| `CoverageQuery` / `CoverageResponse` / `EvidenceItem` / `CoverageTrace` | `application/dto/coverage.py` | Contrato estructurado de entrada/salida (§7.13, §14.5) |
| `KnowledgeRetriever` | `application/reasoning/` | Recupera evidencia con umbral `MIN_SIMILARITY_SCORE` (§14.10) |
| `EvidenceEvaluator` | `application/reasoning/` | Deriva `EvidenceStrength` con reglas explícitas (§14.7) |
| `ReasoningEngine` + `ReasoningContext` | `application/reasoning/` | Sub-orquestador: afiliado → reglas → retrieval → evaluación (§14.2) |
| `CoveragePromptBuilder` (v1.0) | `application/prompts/` | Builder incremental con componentes §8.3–8.9 |
| `ResponseValidator` + `ParsedLLMResponse` | `application/reasoning/` | Validaciones determinísticas (§7.12, §14.15) |
| `AnalyzeCoverageUseCase` | `application/use_cases/` | Punto de entrada único; UNA llamada LLM (§14.6) |

Composition root actualizado con `knowledge_retriever`, `reasoning_engine` y `analyze_coverage_use_case`.

## 2. Decisiones tomadas

1. **Corto-circuito sin LLM ante evidencia INSUFFICIENT** (§7.15/§13.4): si ningún chunk supera el umbral, el sistema responde `INSUFFICIENT_INFORMATION` determinísticamente, sin invocar al modelo. Garantiza "nunca decidir sin evidencia" y ahorra costos. Probado: el stub LLM recibe cero requests.
2. **El prompt nunca transporta identificadores personales** (§9.18): viaja `affiliate_id`, plan, antigüedad, estados y hallazgos — nunca nombre, documento, correo ni teléfono. Hay prueba explícita que lo garantiza.
3. **Los hallazgos determinísticos viajan como "hechos verificados"** en el prompt: el LLM los recibe como insumos confirmados que no debe contradecir, y los bloqueantes se propagan como `warnings` de la respuesta final.
4. **Citas verificables como guardrail principal**: el validador rechaza cualquier cita a un `chunk_id` no suministrado (alucinación detectable determinísticamente) y exige ≥1 cita para toda decisión distinta de `INSUFFICIENT_INFORMATION` (§7.14).
5. **Trazabilidad por consulta** (§7.18/§13.3): `trace_id` UUID + log estructurado JSON (chunks recuperados, citas, modelo, versión de prompt, latencia) + `CoverageTrace` en la respuesta. Sin persistencia dedicada en v1 (decisión V9 del review arquitectónico).
6. **`EvidenceStrength` con reglas publicadas** en `shared/constants/retrieval.py`: INSUFFICIENT (sin chunks) / STRONG (top ≥ 0.45 y ≥2 chunks) / PARTIAL (resto). Ajustable en Fase 8 con datos reales.
7. **Excepción E501 para módulos de prompts**: las líneas de texto natural del prompt no se fragmentan para satisfacer PEP 8; regla documentada en `pyproject.toml`.

## 3. Cobertura de pruebas

25 pruebas nuevas (unitarias, sin red):

- **Retriever**: filtra bajo umbral, vacío cuando nada es relevante.
- **EvidenceEvaluator**: INSUFFICIENT / STRONG / PARTIAL (4 casos).
- **PromptBuilder**: datos de negocio presentes, identificadores personales ausentes, chunk_ids citables, pregunta+formato+guardrails, JSON habilitado.
- **ResponseValidator**: respuesta válida, JSON inválido, campos faltantes, status inválido, cita alucinada, decisión sin citas, INSUFFICIENT sin citas permitido, summary vacío.
- **UseCase**: happy path estructurado con exactamente 1 llamada LLM, corto-circuito sin LLM, afiliado inexistente, findings bloqueantes como warnings, respuesta LLM inválida y cita alucinada → error controlado.

Cobertura `app/application`: **96%** (los misses son ramas de log/errores secundarios).

## 4. Problemas encontrados

- `DeterministicEmbeddingProvider` usaba `hash()` de Python (aleatorizado por proceso): produjo un fallo no reproducible en el test del umbral. Corregido con md5 y 64 dimensiones — los tests son ahora deterministas entre ejecuciones.

## 5. Riesgos

1. **Umbrales de `EvidenceStrength` sin calibrar con embeddings reales**: 0.45 de similitud coseno con `text-embedding-3-small` es un valor inicial razonable pero debe validarse en Fase 8 contra consultas reales.
2. **Sin reintento ante `ResponseValidationError`**: si el LLM devuelve JSON inválido, la consulta falla con error controlado (el controller lo mapeará a 502 en Fase 6). Un retry único sería mejora de Fase 8.
3. **`reference date` por defecto es `date.today()`**: las vigencias de autorizaciones se evalúan contra la fecha del servidor; el dataset sintético tiene corte 2026-06-30, por lo que algunas autorizaciones del Excel estarán vencidas respecto a hoy. Es el comportamiento correcto de negocio, pero puede sorprender en demos.

## 6. Validación contra ESPECIFICACION.md

| Regla | Cumplimiento |
|---|---|
| Contrato `/query` = affiliate_id + question (§14.5) | ✔ `CoverageQuery` |
| Una sola llamada LLM (§14.6) | ✔ probado con stub |
| Decisión preliminar solo datos estructurados (§14.6) | ✔ `EligibilityRules` en el engine |
| EvidenceStrength determinístico (§14.7) | ✔ reglas en constantes |
| Umbral de relevancia (§14.10) | ✔ retriever filtra |
| Builder Pattern para prompts (§3.17, §8.10) | ✔ fluido y componible |
| Prompt versionado (§8.18) | ✔ `PROMPT_VERSION = "1.0"` en trace |
| Guardrails en todas las consultas (§8.9) | ✔ sección obligatoria del builder |
| Validación de respuesta (§7.12) | ✔ determinística v1 (§14.15) |
| Manejo de incertidumbre (§7.15) | ✔ respuesta INSUFFICIENT sin invento |
| Nunca texto plano (§7.13) | ✔ `CoverageResponse` estructurado |
| Trazabilidad (§7.18) | ✔ trace_id + log JSON + DTO |
| Sin datos personales en prompt/logs (§9.18, §14.13) | ✔ probado |
| Separación evidencia/generación (§7.2) | ✔ engine no llama LLM; use case no recupera |

**Conclusión:** Fase 5 cumple la Definition of Done. El sistema responde consultas de cobertura end-to-end (verificado con dobles); la Fase 6 lo expondrá vía API REST.
