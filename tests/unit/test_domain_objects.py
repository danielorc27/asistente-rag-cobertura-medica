"""Pruebas de entidades y value objects del dominio (Fase 2)."""

from datetime import date

import pytest
from app.domain.entities.affiliate import PriorAuthorization
from app.domain.repositories.index_state_repository import IndexManifest
from app.domain.value_objects.document_chunk import DocumentChunk

from tests.fixtures.affiliates import make_affiliate


@pytest.mark.unit
class TestPriorAuthorization:
    def test_validity_window(self) -> None:
        auth = PriorAuthorization(
            service="RM",
            number="AUT-1",
            issued_on=date(2026, 3, 1),
            valid_until=date(2026, 6, 1),
        )
        assert auth.is_valid_on(date(2026, 3, 1))
        assert auth.is_valid_on(date(2026, 6, 1))
        assert not auth.is_valid_on(date(2026, 6, 2))
        assert not auth.is_valid_on(date(2026, 2, 28))


@pytest.mark.unit
class TestAffiliate:
    def test_full_name_and_flags(self) -> None:
        affiliate = make_affiliate()
        assert affiliate.full_name == "Prueba Uno Dos"
        assert affiliate.is_active
        assert not affiliate.is_in_arrears


@pytest.mark.unit
class TestDocumentChunk:
    def test_with_similarity_is_immutable_copy(self) -> None:
        chunk = DocumentChunk(
            chunk_id="c1",
            document_id="d1",
            document_name="DOC1.docx",
            source="documents/DOC1.docx",
            chunk_index=0,
            total_chunks=10,
            content="texto",
        )
        scored = chunk.with_similarity(0.87)
        assert chunk.similarity is None
        assert scored.similarity == 0.87
        assert scored.content == chunk.content


@pytest.mark.unit
class TestIndexManifest:
    def test_compatibility(self) -> None:
        manifest = IndexManifest(
            embedding_model="text-embedding-3-small",
            chunk_size=1000,
            chunk_overlap=200,
            pipeline_version="1",
        )
        assert manifest.is_compatible_with("text-embedding-3-small", 1000, 200)
        assert not manifest.is_compatible_with("text-embedding-3-large", 1000, 200)
        assert not manifest.is_compatible_with("text-embedding-3-small", 500, 200)
