"""Script de operación: construye el índice vectorial (§9.17).

Reutiliza los mismos servicios del sistema; nunca duplica lógica.

Uso:
    uv run python scripts/index_documents.py [--mode full|incremental|new_only]
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.application.dto.indexing import IndexingMode  # noqa: E402
from app.config.dependencies import get_container  # noqa: E402
from app.config.logging import configure_logging  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Indexa los documentos en el vector store.")
    parser.add_argument(
        "--mode",
        choices=[m.value.lower() for m in IndexingMode],
        default="incremental",
        help="Modo de indexación (§6.14). Por defecto: incremental.",
    )
    args = parser.parse_args()

    container = get_container()
    configure_logging(container.settings.log_level, container.settings.log_file)

    report = container.indexing_service.run(IndexingMode(args.mode.upper()))
    print()
    print(report.summary())
    return 1 if report.documents_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
