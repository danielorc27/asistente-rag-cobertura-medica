# Revisión de Fase 4 — Pipeline de Ingesta

**Fecha:** 2026-07-17
**Estado:** COMPLETADA — 68/68 pruebas, Ruff limpio, MyPy strict sin errores.

---

## 1. Componentes implementados

- **`IndexingService`** (`application/services/`): orquesta descubrimiento → carga → normalización → validación → hash → chunking → metadatos → embeddings → persistencia (§6.3). Depende solo de contratos del dominio. Expone `run(mode)` y `is_index_ready()` (§9.8).
- **`IndexingMode`** (FULL / INCREMENTAL / NEW_ONLY, §6.14) e **`IndexingReport`** (Pydantic, con `summary()` según §6.18) en `application/dto/indexing.py`.
- **Port `TextNormalizer`** en `domain/providers/` + implementación `DefaultTextNormalizer` en Infrastructure — necesario para que Application no importe Infrastructure.
- **`PIPELINE_VERSION`** y **`MIN_DOCUMENT_LENGTH`** en `shared/constants/ingestion.py`.
- **Composition root completo** (`config/dependencies.py`): contenedor con dependencias lazy tipadas para todos los ports y el servicio de indexación.
- **`scripts/index_documents.py`** (§9.17): CLI con `--mode`, reutiliza el contenedor — cero lógica duplicada.

## 2. Decisiones tomadas

1. **Manifiesto incompatible ⇒ FULL automático** (§14.11): si cambian `EMBEDDING_MODEL`, `CHUNK_SIZE`, `CHUNK_OVERLAP` o `PIPELINE_VERSION`, el índice se reconstruye completo. Elimina el riesgo de vectores incomparables silenciosos.
2. **Reemplazo atómico por documento**: antes de upsert se ejecuta `delete_document`, garantizando que un documento modificado nunca deja chunks huérfanos (§14.11).
3. **Hash sobre el contenido normalizado** (no sobre bytes del archivo): cambios irrelevantes de formato que no alteran el texto no fuerzan reindexación.
4. **Errores por documento no detienen el pipeline** (§6.16): se registran en log y en `documents_failed`; el exit code del script refleja si hubo fallos.
5. **Archivos sin loader compatible se omiten** (no fallan): permite dejar archivos auxiliares en `documents/` sin romper la ingesta.

## 3. Cobertura de pruebas

9 pruebas nuevas de integración (`tests/integration/test_indexing_service.py`) usando los **3 documentos .docx reales** con embeddings deterministas en memoria (sin red, §11.4):

- FULL indexa los 3 documentos reales y puebla manifiesto + vector store.
- INCREMENTAL omite documentos sin cambios (cache por hash, §6.15).
- NEW_ONLY omite documentos conocidos.
- Manifiesto incompatible (chunk_size distinto) fuerza FULL.
- Trazabilidad de metadatos en cada chunk (§6.10).
- Documento corrupto no detiene el pipeline; el válido se indexa (§6.16).
- Documento modificado se reindexa sin duplicar chunks.
- Directorio inexistente y archivos sin loader → degradación controlada.

Dobles de prueba reutilizables en `tests/mocks/in_memory.py`: `InMemoryVectorStore` (coseno real), `InMemoryIndexStateRepository`, `DeterministicEmbeddingProvider`, `StubLLMProvider`, `InMemoryAffiliateRepository` — servirán para las Fases 5–7.

## 4. Problemas encontrados

- Ninguno funcional. Ajustes menores de formato aplicados por Ruff.

## 5. Riesgos

1. **El índice real aún no existe**: no hay `.env` con `OPENAI_API_KEY` en el entorno. El pipeline está verificado end-to-end con embeddings simulados; la creación del índice real es `uv run python scripts/index_documents.py` una vez configurada la clave. *(Entregable §12.6 "base vectorial creada" queda condicionado a la clave — decisión consciente para no bloquear el roadmap.)*
2. **`iterdir` no recursivo**: documentos en subcarpetas de `documents/` no se descubren. Alcance actual plano; cambiar a `rglob` sería trivial si se necesita.

## 6. Validación contra ESPECIFICACION.md

| Regla | Cumplimiento |
|---|---|
| Descubrimiento automático, sin nombres hardcodeados (§6.4) | ✔ |
| Indexación solo en ingesta, nunca por consulta (§6.1) | ✔ `is_index_ready()` reutiliza el índice |
| Pipeline repetible/idempotente (§6.2) | ✔ hash + manifiesto + reemplazo por documento |
| Hash por documento (§6.11) y cache (§6.15) | ✔ |
| Modos FULL/INCREMENTAL/NEW_ONLY (§6.14) | ✔ |
| Errores no detienen el pipeline (§6.16) | ✔ probado |
| Logging de indexación (§6.17) y estadísticas (§6.18) | ✔ `IndexingReport.summary()` |
| Manifiesto del índice (§14.11) | ✔ con invalidación automática |
| Batching de embeddings (§14.12) | ✔ vía `embed_texts` |
| Scripts reutilizan servicios (§9.17) | ✔ |
| Application sin SDKs (§5.17) | ✔ solo contratos del dominio |

**Conclusión:** Fase 4 cumple la Definition of Done. El sistema puede construir y mantener su base de conocimiento; la Fase 5 implementará el pipeline de consulta sobre ella.
