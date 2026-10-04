"""Constantes del pipeline de consulta.

Reglas explícitas para derivar EvidenceStrength (§14.7). El LLM nunca
produce este valor; se calcula determinísticamente sobre los scores.
"""

# Similitud mínima del mejor chunk para considerar evidencia STRONG.
STRONG_TOP_SIMILARITY = 0.45

# Cantidad mínima de chunks relevantes para considerar evidencia STRONG.
STRONG_MIN_CHUNKS = 2
