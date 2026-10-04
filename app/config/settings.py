"""Configuración centralizada del sistema (§9.5).

Único punto de acceso a variables de entorno. Ninguna otra clase
debe leer ``os.getenv()`` directamente.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración tipada y validada, cargada desde ``.env`` (§9.3)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Proveedores (claves de los factories, §3.15)
    llm_provider: str = Field(default="openai")
    embedding_provider: str = Field(default="openai")
    vector_store_provider: str = Field(default="chroma")

    # OpenAI (o cualquier endpoint compatible: Ollama, Gemini, Azure)
    openai_api_key: str = Field(default="", description="API Key del proveedor LLM.")
    openai_base_url: str = Field(
        default="",
        description=(
            "Endpoint compatible con la API de OpenAI. Vacío = api.openai.com. "
            "Ollama: http://localhost:11434/v1 — Gemini: "
            "https://generativelanguage.googleapis.com/v1beta/openai/"
        ),
    )
    openai_model: str = Field(default="gpt-4.1", description="Modelo LLM por defecto.")
    embedding_model: str = Field(
        default="text-embedding-3-small", description="Modelo de embeddings."
    )
    llm_timeout_seconds: float = Field(default=60.0, gt=0)
    llm_max_retries: int = Field(default=2, ge=0)

    # Documentos y datos
    documents_path: Path = Field(default=Path("documents"))
    affiliates_file: Path = Field(default=Path("data/BD_afiliados.xlsx"))

    # Vector Store
    vector_db_path: Path = Field(default=Path("storage/chroma"))
    top_k_results: int = Field(default=5, ge=1, le=50)
    min_similarity_score: float = Field(default=0.25, ge=0.0, le=1.0)

    # Chunking
    chunk_size: int = Field(default=1000, ge=100)
    chunk_overlap: int = Field(default=200, ge=0)

    # API
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000, ge=1, le=65535)
    debug: bool = Field(default=False)
    reindex_api_key: str = Field(
        default="", description="API Key requerida por POST /reindex (§14.8)."
    )

    # Logging
    log_level: str = Field(default="INFO")
    log_file: Path = Field(default=Path("logs/application.log"))


@lru_cache
def get_settings() -> Settings:
    """Devuelve la configuración como singleton de proceso."""
    return Settings()
