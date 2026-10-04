# Revisión de Fase 6 — API REST

**Fecha:** 2026-07-17
**Estado:** COMPLETADA — 102/102 pruebas, cobertura global 96%, Ruff limpio, MyPy strict sin errores.

---

## 1. Componentes implementados

### Endpoints (§12.8)
| Método | Ruta | Comportamiento |
|---|---|---|
| POST | `/query` | `{affiliate_id, question}` → `QueryResponse` estructurado. 404 si el afiliado no existe; 422 si el body es inválido; 502 ante fallo/respuesta inválida del LLM. |
| POST | `/reindex` | Protegido con header `X-API-Key` (§14.8, comparación en tiempo constante con `secrets.compare_digest`). 401 sin clave o clave errónea; **503 si `REINDEX_API_KEY` no está configurada** (endpoint deshabilitado por defecto). Body `{mode}` opcional (INCREMENTAL por defecto). |
| GET | `/health` | Estado de vector store, repositorio de afiliados, configuración LLM, índice listo, versión (§9.13). `ok`/`degraded`. |
| GET | `/metrics` | Contadores por endpoint, errores por categoría, latencia promedio, uptime (§9.14). |

### Piezas
- `presentation/schemas/`: `QueryRequest/QueryResponse`, `ReindexRequest/Response`, `HealthResponse` — conversión explícita desde DTOs de Application (`from_application`).
- `presentation/controllers/`: `CoverageController`, `AdminController` — sin lógica de negocio; el health hace sondas livianas sin llamar a OpenAI (sin costo por health check).
- `presentation/routers/api_router.py`: registro de endpoints + dependencia de seguridad del reindex.
- `presentation/middleware/`: `error_handlers` (mapa DomainError → HTTP, §9.11) y `metrics_middleware` (latencia y conteo por request).
- `shared/metrics.py`: `MetricsCollector` thread-safe en memoria.
- `main.py`: secuencia de arranque §9.7 — configuración → logging → cableado de controllers → verificación del índice (advierte, **nunca reindexa sola**, §9.9) → rutas.

## 2. Decisiones tomadas

1. **Controllers cableados en `create_app` y expuestos vía `app.state`**: el composition root arma todo; los routers solo consumen. `create_app(container)` acepta un contenedor inyectado — es el mecanismo de prueba E2E sin parches.
2. **Cliente OpenAI lazy**: el SDK exige credenciales al construirse; ahora se difiere al primer uso. La aplicación arranca sin API Key (reporta `llm_configured: false` en health y falla solo la consulta que lo requiera, §9.12).
3. **Errores tipificados nunca exponen internos** (§9.11): respuesta `{error: categoría, detail: mensaje-de-dominio}`; los stack traces quedan solo en logs.
4. **Métricas separadas**: el middleware cuenta requests/latencia; el handler de errores registra la categoría de dominio sin doble conteo de requests.
5. **`/reindex` deshabilitado si no hay clave configurada** (503) en lugar de abierto: seguro por defecto.

## 3. Cobertura de pruebas

9 pruebas E2E nuevas (`tests/e2e/test_api.py`) con la aplicación completa, documentos reales y dependencias simuladas:

- Happy path de `/query` (usa un stub LLM que cita un chunk real del prompt).
- Afiliado inexistente → 404 tipificado; body inválido → 422; LLM inválido → 502.
- `/reindex`: sin clave → 401, clave errónea → 401, sin configurar → 503, clave válida → indexa los 3 documentos reales.
- `/health` completo y `/metrics` con conteos y categorías de error.

**Cobertura global del proyecto: 96%** (1.254 sentencias, 55 sin cubrir).

## 4. Problemas encontrados

- El SDK de OpenAI lanza `Missing credentials` al construir el cliente sin API Key, lo que rompía el arranque del módulo (`app = create_app()`) en entornos sin `.env`. Resuelto con construcción lazy del cliente (decisión 2). Es además el comportamiento correcto de operación.

## 5. Riesgos

1. **`/query` es síncrono** (def, no async): FastAPI lo ejecuta en threadpool, adecuado para esta prueba; alta concurrencia requeriría clientes async (fuera de alcance §9).
2. **Métricas en memoria**: se pierden al reiniciar; suficiente para v1, sustituible por Prometheus sin tocar capas internas.
3. **El health de afiliados lee el Excel en la primera sonda** (carga lazy del repositorio): el primer `/health` puede tardar ~1 s.

## 6. Validación contra ESPECIFICACION.md

| Regla | Cumplimiento |
|---|---|
| Endpoints §12.8 (`/query`, `/reindex`, `/health`, `/metrics`) | ✔ los 4 registrados (verificado vía OpenAPI) |
| Controllers sin lógica de negocio (§12.8) | ✔ delegan a use case / services |
| FastAPI solo en Presentation (§5.3) | ✔ Ruff banned-api lo garantiza |
| Contrato `/query` (§14.5) | ✔ `affiliate_id` + `question` |
| Reindex protegido (§14.8) | ✔ X-API-Key + compare_digest + disabled-by-default |
| Errores clasificados sin internos (§9.11) | ✔ mapa DomainError→HTTP |
| Health (§9.13) y métricas (§9.14) | ✔ |
| Arranque §9.7 con verificación de índice §9.8/§9.9 | ✔ advierte, no reindexa |
| DTOs en cada frontera (§10.16) | ✔ schemas ↔ DTOs de Application |

**Conclusión:** Fase 6 cumple la Definition of Done. El sistema es operable por HTTP de punta a punta.
