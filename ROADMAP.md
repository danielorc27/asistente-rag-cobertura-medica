# ROADMAP.md — Estado de Ejecución

Roadmap oficial definido en ESPECIFICACION.md §12. Estado al 2026-07-17:

| Fase | Alcance | Estado | Revisión |
|---|---|---|---|
| 0 | Revisión arquitectónica del ESPECIFICACION.md | ✅ Aprobada con decisiones | [ARCHITECTURE_REVIEW.md](ARCHITECTURE_REVIEW.md) |
| 1 | Inicialización (uv, ruff, mypy, pytest, settings, logging, DI) | ✅ Completada | — |
| 2 | Dominio (entidades, VOs, ports, reglas, excepciones) | ✅ Completada | [REVIEW_PHASE_2.md](REVIEW_PHASE_2.md) |
| 3 | Infraestructura (Word, Excel, OpenAI, Chroma, factories) | ✅ Completada | [REVIEW_PHASE_3.md](REVIEW_PHASE_3.md) |
| 4 | Pipeline de ingesta (hash, manifiesto, modos, CLI) | ✅ Completada | [REVIEW_PHASE_4.md](REVIEW_PHASE_4.md) |
| 5 | Pipeline de consulta (reasoning, prompts, validador, use case) | ✅ Completada | [REVIEW_PHASE_5.md](REVIEW_PHASE_5.md) |
| 6 | API REST (/query, /reindex, /health, /metrics) | ✅ Completada | [REVIEW_PHASE_6.md](REVIEW_PHASE_6.md) |
| 7 | Testing consolidado (110+ pruebas, casos límite, golden set) | ✅ Completada | [REVIEW_PHASE_7.md](REVIEW_PHASE_7.md) |
| 8 | Optimización (dedup de contexto, retry LLM) | ✅ Completada | [REVIEW_PHASE_8.md](REVIEW_PHASE_8.md) |
| 9 | Documentación y entrega (Docker, ARCHITECTURE, CHANGELOG) | ✅ Completada | este documento |

## Tareas operativas post-entrega (requieren OPENAI_API_KEY)

1. `copy .env.example .env` y completar `OPENAI_API_KEY` y `REINDEX_API_KEY`.
2. `uv run python scripts/index_documents.py` — construir el índice real.
3. `uv run python scripts/evaluate_golden_set.py` — evaluar los 10 casos del golden set con el LLM real.
4. Calibrar `MIN_SIMILARITY_SCORE` y los umbrales de `EvidenceStrength` con los scores reales observados.

## Evolución futura prevista por la arquitectura (§12.18)

- Nuevos LLM/embeddings/vector stores: nueva clase + factory + variable de entorno.
- Nuevos formatos documentales: nuevo `DocumentLoader`.
- Afiliados en PostgreSQL/API: nuevo `AffiliateRepository`.
- Sistema agéntico: el `ReasoningEngine` es el punto de extensión (§7.17) sin tocar API ni use cases.
- Validación semántica anti-alucinación con LLM juez (declarada fuera de v1, Addendum 14.15).
