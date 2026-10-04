# Asistente de Validación de Cobertura (RAG)

Asistente inteligente que determina si un procedimiento médico solicitado por un
afiliado está cubierto por su plan de salud, cruzando documentos normativos
(RAG sobre ChromaDB) con los datos estructurados del afiliado.

## Arquitectura

Clean Architecture con dependencias apuntando al dominio:

```
Presentation → Application → Domain ← Infrastructure
```

Especificación completa en [ESPECIFICACION.md](ESPECIFICACION.md) (incluye el Addendum de
decisiones aprobadas, cap. 14) y revisión arquitectónica en
[ARCHITECTURE_REVIEW.md](ARCHITECTURE_REVIEW.md).

## Requisitos

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- API Key de OpenAI

## Instalación

```bash
uv sync
copy .env.example .env   # y completar OPENAI_API_KEY
```

## Uso

```bash
# Indexar documentos (una sola vez o tras cambios en documents/)
uv run python scripts/index_documents.py

# Levantar la API
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Proveedores LLM alternativos

El proveedor se selecciona por configuración, sin tocar código (§2.13):

| Escenario | Configuración en `.env` |
|---|---|
| **Sin ninguna API Key (modo demo offline)** | `LLM_PROVIDER=mock` y `EMBEDDING_PROVIDER=mock` |
| **Ollama (local)** | `OPENAI_BASE_URL=http://localhost:11434/v1`, `OPENAI_API_KEY=ollama`, `OPENAI_MODEL=llama3.1`, `EMBEDDING_MODEL=nomic-embed-text` |
| **Gemini** | `OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/`, `OPENAI_API_KEY=<GEMINI_API_KEY>`, `OPENAI_MODEL=gemini-2.5-flash`, `EMBEDDING_MODEL=gemini-embedding-001` |
| OpenAI (por defecto) | `OPENAI_API_KEY=<clave>` |

En modo `mock` el sistema completo funciona (ingesta, retrieval, API), pero las
respuestas quedan marcadas como SIMULADAS con status `INSUFFICIENT_INFORMATION`:
el mock demuestra el pipeline, nunca fabrica decisiones de cobertura.

**Importante:** al cambiar de `EMBEDDING_MODEL` o de proveedor de embeddings, el
manifiesto detecta la incompatibilidad y fuerza reindexación FULL automática.

### Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Interfaz web para probar consultas desde el navegador |
| POST | `/query` | Consulta de cobertura (`affiliate_id` + `question`) |
| POST | `/reindex` | Reindexación (requiere header `X-API-Key`) |
| GET | `/health` | Estado del servicio y sus dependencias |
| GET | `/metrics` | Métricas de operación |

Con la API levantada, abre `http://localhost:8000/` para consultar desde una
interfaz web sencilla, o `http://localhost:8000/docs` para el Swagger UI.

### Docker (§9.16)

```bash
docker compose -f docker/docker-compose.yml up --build
```

## Calidad

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest --cov=app     # 113 pruebas, 100% offline (sin OpenAI real)
```

## Evaluación con LLM real

Con `OPENAI_API_KEY` configurada e índice construido:

```bash
uv run python scripts/evaluate_golden_set.py
```

Ejecuta los 10 casos de `tests/fixtures/golden_set.json` por el flujo completo
y reporta PASS/FAIL por caso (§11.19).

## Documentación

| Documento | Contenido |
|---|---|
| [ESPECIFICACION.md](ESPECIFICACION.md) | Especificación normativa (incluye Addendum de decisiones, cap. 14) |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Vista ejecutable de la arquitectura y flujos |
| [ARCHITECTURE_REVIEW.md](ARCHITECTURE_REVIEW.md) | Revisión arquitectónica previa a la implementación |
| [ROADMAP.md](ROADMAP.md) | Estado de fases y tareas post-entrega |
| [CHANGELOG.md](CHANGELOG.md) | Historial de cambios |
| REVIEW_PHASE_2..8.md | Revisión de cierre de cada fase |

## Estructura

```
app/
├── presentation/    # API REST (FastAPI): routers, controllers, schemas
├── application/     # Use cases, reasoning engine, prompts, DTOs
├── domain/          # Entidades, value objects, contratos (ports), reglas puras
├── infrastructure/  # Adapters: OpenAI, Chroma, Excel, Word, chunking
├── shared/          # Tipos y constantes reutilizables
└── config/          # Settings, logging, composition root (DI)
```
