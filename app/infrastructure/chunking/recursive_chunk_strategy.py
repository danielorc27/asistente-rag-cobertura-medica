"""Estrategia de chunking recursivo por caracteres (§6.8)."""

from app.domain.providers.chunk_strategy import ChunkStrategy

_DEFAULT_SEPARATORS: tuple[str, ...] = ("\n\n", "\n", ". ", " ")


class RecursiveChunkStrategy(ChunkStrategy):
    """Divide texto respetando jerarquía semántica: párrafos → líneas → oraciones.

    Garantiza (§6.9): nunca divide palabras, mantiene overlap configurable
    y no pierde contenido.
    """

    def __init__(
        self,
        chunk_size: int,
        chunk_overlap: int,
        separators: tuple[str, ...] = _DEFAULT_SEPARATORS,
    ) -> None:
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap debe ser menor que chunk_size")
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._separators = separators

    def split(self, text: str) -> list[str]:
        text = text.strip()
        if not text:
            return []
        fragments = self._split_recursive(text, self._separators)
        return self._merge(fragments)

    def _split_recursive(self, text: str, separators: tuple[str, ...]) -> list[str]:
        if len(text) <= self._chunk_size:
            return [text]
        if not separators:
            # Último recurso: cortar por espacios en ventanas del tamaño máximo.
            words = text.split(" ")
            pieces: list[str] = []
            current = ""
            for word in words:
                candidate = f"{current} {word}".strip()
                if len(candidate) > self._chunk_size and current:
                    pieces.append(current)
                    current = word
                else:
                    current = candidate
            if current:
                pieces.append(current)
            return pieces

        head, tail = separators[0], separators[1:]
        parts = [part for part in text.split(head) if part.strip()]
        if len(parts) <= 1:
            return self._split_recursive(text, tail)

        pieces = []
        for part in parts:
            if len(part) > self._chunk_size:
                pieces.extend(self._split_recursive(part, tail))
            else:
                pieces.append(part.strip())
        return pieces

    def _merge(self, fragments: list[str]) -> list[str]:
        chunks: list[str] = []
        current = ""
        for fragment in fragments:
            candidate = f"{current}\n{fragment}".strip() if current else fragment
            if len(candidate) <= self._chunk_size:
                current = candidate
                continue
            if current:
                chunks.append(current)
            overlap = self._overlap_tail(current)
            current = f"{overlap}\n{fragment}".strip() if overlap else fragment
        if current:
            chunks.append(current)
        return chunks

    def _overlap_tail(self, chunk: str) -> str:
        """Cola de overlap cortada en límite de palabra (§6.9)."""
        if not chunk or not self._chunk_overlap:
            return ""
        tail = chunk[-self._chunk_overlap :]
        if len(tail) < len(chunk) and " " in tail:
            tail = tail.split(" ", 1)[1]
        return tail.strip()
