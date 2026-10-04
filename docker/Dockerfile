# Imagen de la API de validación de cobertura (§9.16).
# Build (desde la raíz del proyecto):
#   docker build -f docker/Dockerfile -t coverage-assistant .

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1

WORKDIR /app

RUN pip install --no-cache-dir uv

# Dependencias primero para aprovechar el cache de capas.
COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev --no-install-project

# Código y recursos.
COPY app ./app
COPY scripts ./scripts
COPY documents ./documents
COPY data ./data
RUN uv sync --no-dev

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
