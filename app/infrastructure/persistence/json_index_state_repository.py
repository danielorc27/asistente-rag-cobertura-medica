"""Persistencia del manifiesto del índice en JSON (§14.11)."""

import json
import logging
from dataclasses import asdict
from pathlib import Path

from app.domain.repositories.index_state_repository import IndexManifest, IndexStateRepository

logger = logging.getLogger(__name__)


class JsonIndexStateRepository(IndexStateRepository):
    """Guarda el manifiesto como JSON junto al índice vectorial."""

    def __init__(self, manifest_path: Path) -> None:
        self._path = manifest_path

    def load(self) -> IndexManifest | None:
        if not self._path.exists():
            return None
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
            return IndexManifest(
                embedding_model=raw["embedding_model"],
                chunk_size=int(raw["chunk_size"]),
                chunk_overlap=int(raw["chunk_overlap"]),
                pipeline_version=str(raw["pipeline_version"]),
                documents=dict(raw.get("documents", {})),
            )
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            logger.warning("Manifiesto de índice corrupto (%s); se ignorará.", exc)
            return None

    def save(self, manifest: IndexManifest) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._path.with_suffix(".tmp")
        tmp.write_text(json.dumps(asdict(manifest), indent=2), encoding="utf-8")
        tmp.replace(self._path)
        logger.info("Manifiesto de índice guardado (%d documentos).", len(manifest.documents))
