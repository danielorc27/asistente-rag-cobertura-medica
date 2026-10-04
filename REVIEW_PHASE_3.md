# Revisión de Fase 3 — Infraestructura

**Fecha:** 2026-07-17
**Estado:** COMPLETADA — 59/59 pruebas, Ruff limpio, MyPy strict sin errores, cobertura de infraestructura 89%.

---

## 1. Componentes implementados

| Componente | Módulo | Contrato que implementa |
|---|---|---|
| `WordDocumentLoader` | `infrastructure/document_loader/` | `DocumentLoader` |
| `TextNormalizer` | `infrastructure/parser/` | etapa de normalización (§6.6) |
| `RecursiveChunkStrategy` | `infrastructure/chunking/` | `ChunkStrategy` |
| `ExcelAffiliateRepository` | `infrastructure/repositories/` | `AffiliateRepository` |
| `OpenAIProvider` | `infrastructure/llm/` | `LLMProvider` |
| `OpenAIEmbeddingProvider` | `infrastructure/embeddings/` | `EmbeddingProvider` |
| `ChromaVectorStore` | `infrastructure/vectorstore/` | `VectorStore` |
| `JsonIndexStateRepository` | `infrastructure/persistence/` | `IndexStateRepository` (§14.11) |
| Factories de proveedores | `infrastructure/factories/` | §3.15, seleccionables por configuración |

Variables de entorno nuevas: `LLM_PROVIDER`, `EMBEDDING_PROVIDER`, `VECTOR_STORE_PROVIDER`, `LLM_TIMEOUT_SECONDS`, `LLM_MAX_RETRIES` (reflejadas en `.env.example`).

## 2. Decisiones tomadas

1. **El loader Word extrae tablas en orden de aparición.** DOC1 (5 tablas) y DOC2 (2 tablas) contienen los esquemas de copagos y carencias en tablas; se recorren los bloques del XML (`w:p`/`w:tbl`) para preservar el orden y las tablas se serializan como filas `celda | celda`. Los headings se marcan con prefijo Markdown (`#`, `##`) para conservar la estructura semántica útil al chunking y al LLM.
2. **Similitud expuesta al dominio = `1 − distancia coseno`** (0..1, mayor es mejor), independiente del motor vectorial. Cualquier reemplazo de Chroma debe conservar esa semántica.
3. **Clientes OpenAI inyectables en pruebas** (parámetro `client`): permite cumplir §11.4 (nunca OpenAI real en tests) sin monkeypatching frágil. Timeout y reintentos se delegan al SDK (`timeout`, `max_retries`).
4. **Batching de embeddings en lotes de 100** con reordenamiento por índice de respuesta (§14.12).
5. **Mapeo Excel validado**: cualquier valor inesperado (fecha inválida, Sí/No desconocido, autorización inconsistente) produce `AffiliateDataError` con el id del afiliado — nunca corrupción silenciosa. Los campos de autorización se colapsan en el value object `PriorAuthorization`.
6. **Manifiesto con escritura atómica** (archivo temporal + `replace`) y tolerancia a corrupción (devuelve `None` y se registra warning → fuerza reindexación).
7. **Enums del dominio migrados a `StrEnum`** (Python 3.11+) por recomendación del linter.

## 3. Cobertura de pruebas

38 pruebas nuevas (24 unitarias + 14 de integración). Cobertura de `app/infrastructure`: **89%**.

- Unitarias: chunker (tamaño, overlap, no pérdida, no divide palabras, validación de parámetros), normalizador, providers OpenAI con clientes fake (metadatos, formato JSON, respuesta vacía, fallo del SDK, orden de embeddings, batching), factories (proveedor desconocido → `ConfigurationError`).
- Integración (con recursos reales locales): `WordDocumentLoader` contra `DOC1` real **verificando que las tablas sobreviven a la extracción**; `ExcelAffiliateRepository` contra `BD_afiliados.xlsx` real (afiliado con autorización, sin autorización, retirado en mora, inexistente → `None`); `ChromaVectorStore` con persistencia temporal (upsert/search/similarity/delete por documento/persistencia entre instancias); manifiesto (roundtrip, ausente, corrupto).

## 4. Problemas encontrados

1. **Corrupción de encoding por PowerShell**: un reemplazo de texto con `Get-Content`/`Set-Content` produjo mojibake en los enums del dominio (`"Al día"` → `"Al dÃ­a"`), lo que habría roto el mapeo del Excel silenciosamente. Detectado y corregido reescribiendo los archivos con UTF-8 limpio. Lección operativa: ediciones de archivos solo con herramientas que preservan UTF-8.
2. **MyPy vs stubs del SDK**: las firmas tipadas de `openai` exigen `ChatCompletionMessageParam` y un `response_format` no-None; se ajustó el adapter. Chroma requiere `cast` en las fronteras de `embeddings` (invarianza de `list`); casts localizados y justificados solo en el módulo adapter.
3. `python_version` de MyPy se subió a 3.12 porque los stubs de numpy (dependencia transitiva de Chroma) usan sintaxis 3.12; el código sigue siendo compatible 3.11+.

## 5. Riesgos

1. **El separador `. ` del chunker** puede cortar oraciones con abreviaturas ("Dr. Pérez"); impacto bajo para estos documentos. Se revisará en Fase 8 con retrieval real.
2. **`ExcelAffiliateRepository` carga el archivo completo en memoria** (1.000 filas — trivial). Para volúmenes reales, la interfaz permite sustituirlo por PostgreSQL sin tocar otras capas (§2.9).
3. **Los tests de integración de Chroma añaden ~20 s** a la suite por la inicialización del cliente; aceptable, y los unitarios siguen siendo rápidos (<2 s).
4. **`delete_document` de Chroma con `where`** depende del metadato `document_id`; la prueba de integración lo cubre para prevenir regresiones si cambia la versión de Chroma.

## 6. Validación contra ESPECIFICACION.md

| Regla | Cumplimiento |
|---|---|
| SDKs solo en Infrastructure (§5.16/§5.17) | ✔ verificado por Ruff banned-api + test de pureza del dominio |
| Adapter Pattern sobre cada SDK (§3.16) | ✔ OpenAI/Chroma/pandas/python-docx nunca salen de sus módulos |
| Pandas solo en `ExcelAffiliateRepository` (§5.10) | ✔ |
| ChromaDB solo en `infrastructure/vectorstore` (§5.8) | ✔ |
| Factories por configuración (§3.15) | ✔ con error controlado ante proveedor desconocido |
| Modelos nunca hardcodeados (§5.6/§5.7) | ✔ llegan por `Settings` |
| Manejo de errores tipificado (§9.11) | ✔ todas las fallas se traducen a excepciones del dominio |
| Pruebas sin OpenAI real (§11.4) | ✔ clientes fake inyectados |
| Trazabilidad de chunks (§6.10) | ✔ metadatos completos en el vector store |
| Pruebas por fase (§14.9) | ✔ 38 pruebas entregadas con la fase |

**Conclusión:** la Fase 3 cumple la Definition of Done (§12.14). Todos los contratos del dominio tienen implementación funcional verificada contra los insumos reales de la prueba.
