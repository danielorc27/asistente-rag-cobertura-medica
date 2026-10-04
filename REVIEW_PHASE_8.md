# Revisión de Fase 8 — Optimización

**Fecha:** 2026-07-17
**Estado:** COMPLETADA — 113/113 pruebas, Ruff limpio, MyPy strict sin errores.

---

## 1. Optimizaciones aplicadas

1. **Deduplicación de contexto en el retriever (§8.13).** Los chunks recuperados con contenido idéntico (tras normalizar espacios/mayúsculas) se eliminan conservando el de mayor relevancia. Efecto: mejor relación señal/ruido en el prompt y menos tokens por consulta. Nota: el overlap de chunking puede producir fragmentos casi idénticos en documentos con texto repetitivo.
2. **Reintento único ante respuesta LLM inválida (§9.12).** Si el `ResponseValidator` rechaza la salida (JSON malformado, cita alucinada, status inválido), el use case reintenta exactamente una vez antes de emitir el error controlado 502. Cierra el riesgo #2 de la revisión de Fase 5. El límite de un reintento evita loops de costo.

## 2. Optimizaciones evaluadas y descartadas (con justificación)

- **Cache de embeddings de consulta**: las consultas de usuarios rara vez se repiten textualmente; complejidad sin beneficio medible (§10.6 YAGNI).
- **Re-ranking con cross-encoder**: agregaría una dependencia pesada para 3 documentos; el umbral + top_k es suficiente para este corpus (§13.9).
- **Ajuste de umbrales de EvidenceStrength y MIN_SIMILARITY_SCORE**: requiere mediciones con embeddings reales (API Key). Los valores son configurables por entorno, así que la calibración es operativa, no de código. Documentado como tarea operativa post-entrega.
- **Clientes async**: fuera de alcance (§9 — sin escalamiento distribuido).

## 3. Pruebas

3 pruebas nuevas: deduplicación conservando el más relevante; reintento que recupera la consulta (2 llamadas exactas); doble fallo → error controlado sin tercer intento.

## 4. Riesgos

- El reintento duplica el costo en el peor caso; mitigado por ser único y solo ante validación fallida (evento raro con `response_format=json_object`).

## 5. Validación contra ESPECIFICACION.md

- §8.13 (gestión del contexto: eliminar duplicados, priorizar relevantes) ✔
- §9.12 (recuperación automática cuando sea posible) ✔
- §14.6 se preserva: sigue habiendo UNA llamada lógica al LLM por consulta; el reintento es la política de recuperación ante fallo, no una segunda consulta de razonamiento.
- KISS/YAGNI (§10.5–10.6): optimizaciones especulativas descartadas y documentadas ✔
