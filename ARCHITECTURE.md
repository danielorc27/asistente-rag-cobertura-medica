# ARCHITECTURE.md — Asistente de Validación de Cobertura

Resumen ejecutable de la arquitectura. La especificación normativa completa es
[ESPECIFICACION.md](ESPECIFICACION.md) (incluido el Addendum cap. 14 con las decisiones de la
revisión arquitectónica registrada en [ARCHITECTURE_REVIEW.md](ARCHITECTURE_REVIEW.md)).

## 1. Vista de capas

```
Presentation  →  Application  →  Domain  ←  Infrastructure
(FastAPI)        (use cases,      (entidades,   (OpenAI, Chroma,
                  reasoning,       contratos,    pandas, python-docx)
                  prompts, DTOs)   reglas puras)
```

- Toda dependencia apunta al dominio. Infrastructure **implementa** los
  contratos (`domain/repositories`, `domain/providers`); nunca es destino de
  una dependencia del dominio.
- `config/dependencies.py` es el **composition root**: único módulo autorizado
  a importar de todas las capas para cablear implementaciones.
- Garantías ejecutables: reglas `banned-api` de Ruff por capa +
  `tests/unit/test_domain_purity.py` (verificación AST de que el dominio solo
  importa stdlib).

## 2. Flujo de consulta (POST /query)

```
QueryRequest {affiliate_id, question}
  → CoverageController
  → AnalyzeCoverageUseCase
      → ReasoningEngine
          → AffiliateRepository.find_by_id()        (Excel)
          → EligibilityRules.evaluate()              (reglas determinísticas, Domain)
          → KnowledgeRetriever.retrieve()            (embedding + Chroma + umbral + dedup)
          → EvidenceEvaluator.evaluate()             (EvidenceStrength por reglas)
      → [INSUFFICIENT → respuesta determinística SIN llamar al LLM]
      → CoveragePromptBuilder (v1.0)                 (system + razonamiento + evidencia
                                                      + afiliado + formato + guardrails)
      → LLMProvider.generate()                       (UNA llamada; retry único si inválida)
      → ResponseValidator                            (JSON, status, citas ⊆ chunks)
  → CoverageResponse {status, summary, reasoning, evidence[], evidence_strength,
                      warnings[], trace{trace_id, model, prompt_version, ...}}
```

Principios operativos:
- **El LLM nunca es fuente de verdad**: solo interpreta la evidencia recuperada
  y los datos estructurados del afiliado.
- **Toda decisión cita evidencia**; una cita a un chunk no suministrado se
  rechaza (guardrail determinístico contra alucinaciones).
- **La incertidumbre es un resultado válido**: sin evidencia sobre el umbral,
  el sistema responde `INSUFFICIENT_INFORMATION` sin gastar tokens.

## 3. Flujo de ingesta (scripts/index_documents.py, POST /reindex)

```
documents/*.docx → DocumentLoader (párrafos + TABLAS en orden)
                → TextNormalizer → validación → hash SHA-256
                → RecursiveChunkStrategy (CHUNK_SIZE/CHUNK_OVERLAP)
                → EmbeddingProvider (batch) → ChromaVectorStore (upsert)
                → IndexManifest (modelo, parámetros, hashes por documento)
```

- Modos: `FULL` / `INCREMENTAL` (hash) / `NEW_ONLY`.
- El manifiesto invalida el índice si cambian `EMBEDDING_MODEL`,
  `CHUNK_SIZE`, `CHUNK_OVERLAP` o la versión del pipeline → FULL automático.
- Un documento que falla no detiene la ingesta.

## 4. Contratos (ports) y adapters

| Port (Domain) | Adapter v1 (Infrastructure) | Sustitutos previstos |
|---|---|---|
| `LLMProvider` | `OpenAIProvider` (GPT-4.1) | Gemini, Mistral, Azure |
| `EmbeddingProvider` | `OpenAIEmbeddingProvider` | Voyage, Cohere, ST |
| `VectorStore` | `ChromaVectorStore` | Pinecone, Qdrant, FAISS |
| `AffiliateRepository` | `ExcelAffiliateRepository` | PostgreSQL, API REST |
| `DocumentLoader` | `WordDocumentLoader` | PDF, HTML, Markdown |
| `ChunkStrategy` | `RecursiveChunkStrategy` | Semántico, por oraciones |
| `TextNormalizer` | `DefaultTextNormalizer` | — |
| `IndexStateRepository` | `JsonIndexStateRepository` | — |

Cambiar un proveedor = nueva clase en Infrastructure + registro en el factory
+ variable de entorno. Cero cambios en Domain/Application/Presentation.

## 5. Decisiones clave (registro)

1. Dirección de dependencias corregida en revisión: `Domain ← Infrastructure` (Addendum 14.1).
2. Un solo orquestador: `AnalyzeCoverageUseCase`; `ReasoningEngine` como sub-orquestador (14.2). `CoverageAnalysisService` eliminado.
3. `/query` recibe `affiliate_id` estructurado — nunca se resuelve el afiliado por nombre en texto libre (14.5).
4. Una llamada LLM por consulta; Intent Analyzer determinístico (14.6).
5. `EvidenceStrength` (INSUFFICIENT/PARTIAL/STRONG) por reglas explícitas en lugar de confidence numérico (14.7).
6. `/reindex` protegido con `X-API-Key`; deshabilitado (503) si no hay clave configurada (14.8).
7. Datos personales del afiliado nunca viajan al prompt ni a logs (filtro de redacción + prueba dedicada).
8. Testing por fase + consolidación E2E final (14.9).

## 6. Observabilidad y errores

- Logging centralizado con filtro de datos sensibles (`config/logging.py`).
- Traza JSON por consulta: `trace_id`, chunks, citas, modelo, versión de prompt, latencia.
- `/metrics`: requests, errores por categoría, latencia promedio, uptime.
- Errores del dominio → HTTP: 404 afiliado, 502 LLM/validación, 503 configuración; nunca stack traces al cliente.

## 7. Estructura de carpetas

Ver [README.md](README.md#estructura). Regla: si no es obvio dónde va un
archivo nuevo en <1 minuto, la estructura debe revisarse (§4.14).
