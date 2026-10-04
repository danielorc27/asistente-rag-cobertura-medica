# CHANGELOG

Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.1.0/).

## [0.2.0] — 2026-07-17

### Añadido
- `OPENAI_BASE_URL`: permite usar cualquier endpoint compatible con la API de OpenAI (Ollama local, Gemini, Azure) cambiando solo configuración.
- Modo demo offline: `LLM_PROVIDER=mock` y `EMBEDDING_PROVIDER=mock` ejecutan el sistema completo sin ninguna API Key; las respuestas quedan marcadas como SIMULADAS y nunca emiten decisiones de cobertura.
- Prueba E2E del modo mock con cableado real de factories (sin dobles de test), incluida indexación en Chroma real.

### Corregido (integración real con Gemini)
- `OpenAIEmbeddingProvider`: los endpoints compatibles (Gemini) devuelven `index=None` en los embeddings; ahora se preserva el orden de la respuesta en ese caso.
- `VectorStore.reset()` (nuevo método del contrato): la reindexación FULL recrea la colección completa — necesario porque cambiar de proveedor de embeddings cambia la dimensionalidad de los vectores (256 mock → 3072 Gemini).
- `scripts/evaluate_golden_set.py`: opción `--pause` para respetar límites de cuota (free tier de Gemini: 5 solicitudes/minuto).

### Verificado
- Golden set 10/10 con `gemini-3.5-flash` + `gemini-embedding-001` reales (2026-07-17).

## [0.3.0] — 2026-07-17

### Añadido
- Interfaz web mínima en `GET /` (`app/presentation/static/index.html`): formulario de consulta que consume `POST /query` y presenta la decisión con su evidencia citada, advertencias y trazabilidad. HTML/CSS/JS puro servido por FastAPI — sin dependencias nuevas ni build.

## [0.1.0] — 2026-07-17

Primera versión funcional completa de la prueba técnica.

### Añadido
- Revisión arquitectónica del ESPECIFICACION.md con 6 decisiones aprobadas (Addendum cap. 14).
- Estructura Clean Architecture: `presentation / application / domain / infrastructure / shared / config` con composition root explícito.
- Dominio: entidades (`Affiliate`, `Document`, `PreliminaryAssessment`), value objects (`DocumentChunk`, enums `CoverageStatus`, `EvidenceStrength`), reglas determinísticas (`EligibilityRules`), 8 contratos (ports) y jerarquía de excepciones.
- Infraestructura: `WordDocumentLoader` (con extracción de tablas en orden), `ExcelAffiliateRepository` (mapeo validado del BD_afiliados real), `OpenAIProvider` y `OpenAIEmbeddingProvider` (clientes lazy, batching), `ChromaVectorStore`, `JsonIndexStateRepository`, factories por configuración.
- Pipeline de ingesta idempotente: hash SHA-256, manifiesto de índice con invalidación automática, modos FULL/INCREMENTAL/NEW_ONLY, CLI `scripts/index_documents.py`.
- Pipeline de consulta: retriever con umbral y deduplicación, `EvidenceEvaluator` (EvidenceStrength por reglas), `CoveragePromptBuilder` v1.0 (modular, versionado, con guardrails), `ResponseValidator` (citas verificables), `AnalyzeCoverageUseCase` con una sola llamada LLM, corto-circuito sin evidencia y reintento único ante respuesta inválida.
- API REST: `POST /query`, `POST /reindex` (X-API-Key), `GET /health`, `GET /metrics`; manejo tipificado de errores y middleware de métricas.
- Seguridad: filtro de datos sensibles en logs, prompt sin identificadores personales, reindex deshabilitado por defecto.
- Testing: 113 pruebas (unit/integration/e2e) 100% offline, cobertura 96%, golden set de 10 casos + script de evaluación contra el sistema real.
- Docker: `docker/Dockerfile` y `docker/docker-compose.yml`.
- Documentación: README, ARCHITECTURE.md, ROADMAP.md, revisiones por fase (REVIEW_PHASE_2..8).

### Decisiones registradas
- `Domain ← Infrastructure` (corrección de dirección de dependencias).
- `EvidenceStrength` en lugar de porcentaje de confianza.
- `affiliate_id` estructurado en `/query` (nunca resolución por nombre).
- Testing por fase; consolidación E2E al final.
