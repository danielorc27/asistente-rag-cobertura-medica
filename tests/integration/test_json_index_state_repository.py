"""Pruebas del repositorio de manifiesto del índice (§14.11)."""

from pathlib import Path

import pytest
from app.domain.repositories.index_state_repository import IndexManifest
from app.infrastructure.persistence.json_index_state_repository import JsonIndexStateRepository


@pytest.mark.integration
class TestJsonIndexStateRepository:
    def test_roundtrip(self, tmp_path: Path) -> None:
        repo = JsonIndexStateRepository(manifest_path=tmp_path / "manifest.json")
        manifest = IndexManifest(
            embedding_model="text-embedding-3-small",
            chunk_size=1000,
            chunk_overlap=200,
            pipeline_version="1",
            documents={"DOC1.docx": "hash1"},
        )
        repo.save(manifest)
        loaded = repo.load()
        assert loaded == manifest

    def test_load_missing_returns_none(self, tmp_path: Path) -> None:
        repo = JsonIndexStateRepository(manifest_path=tmp_path / "manifest.json")
        assert repo.load() is None

    def test_corrupt_manifest_returns_none(self, tmp_path: Path) -> None:
        path = tmp_path / "manifest.json"
        path.write_text("{no es json", encoding="utf-8")
        assert JsonIndexStateRepository(manifest_path=path).load() is None
