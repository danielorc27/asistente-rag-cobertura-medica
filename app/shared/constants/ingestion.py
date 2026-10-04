"""Constantes del pipeline de ingesta."""

# Versión del pipeline: forma parte del manifiesto del índice (§14.11).
# Incrementarla invalida índices previos y fuerza reindexación FULL.
PIPELINE_VERSION = "1.0"

# Umbral de validación (§6.7): un documento con menos caracteres útiles
# se considera vacío/ilegible y se omite con registro en logs.
MIN_DOCUMENT_LENGTH = 50
