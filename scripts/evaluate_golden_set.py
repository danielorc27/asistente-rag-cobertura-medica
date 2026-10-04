"""Evaluación del golden set contra el sistema real (§8.19, §11.19).

Requiere OPENAI_API_KEY en .env e índice construido
(``python scripts/index_documents.py``). Ejecuta cada caso del golden set
por el flujo completo (use case real, LLM real) y reporta el resultado.

Uso:
    uv run python scripts/evaluate_golden_set.py
"""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.application.dto.coverage import CoverageQuery  # noqa: E402
from app.config.dependencies import get_container  # noqa: E402
from app.config.logging import configure_logging  # noqa: E402
from app.domain.exceptions.errors import AffiliateNotFoundError, DomainError  # noqa: E402

GOLDEN_SET = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "golden_set.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Evalúa el golden set contra el sistema real.")
    parser.add_argument(
        "--pause",
        type=float,
        default=0.0,
        help="Segundos de espera entre casos (p. ej. 13 para el free tier de Gemini, 5 RPM).",
    )
    args = parser.parse_args()

    container = get_container()
    configure_logging(container.settings.log_level, container.settings.log_file)

    if not container.indexing_service.is_index_ready():
        print("ERROR: el índice no está construido. Ejecute scripts/index_documents.py primero.")
        return 2

    cases = json.loads(GOLDEN_SET.read_text(encoding="utf-8"))["cases"]
    use_case = container.analyze_coverage_use_case
    passed = 0
    results: list[str] = []

    for position, case in enumerate(cases):
        if args.pause and position:
            time.sleep(args.pause)
        case_id = case["id"]
        try:
            response = use_case.execute(
                CoverageQuery(affiliate_id=case["affiliate_id"], question=case["question"])
            )
        except AffiliateNotFoundError:
            ok = case.get("expected_http") == 404
            results.append(_line(case_id, ok, "404 afiliado inexistente"))
            passed += ok
            continue
        except DomainError as exc:
            results.append(_line(case_id, False, f"error: {exc}"))
            continue

        status_ok = response.status.value in case.get("expected_status", [])
        evidence_ok = bool(response.evidence) == case.get("expect_evidence", True)
        ok = status_ok and evidence_ok
        detail = (
            f"status={response.status.value} strength={response.evidence_strength.value} "
            f"citas={len(response.evidence)}"
        )
        if not status_ok:
            detail += f" (esperado: {case.get('expected_status')})"
        results.append(_line(case_id, ok, detail))
        passed += ok

    print("\n=== Golden Set — Resultados ===")
    print("\n".join(results))
    print(f"\nTotal: {passed}/{len(cases)} casos aceptados")
    return 0 if passed == len(cases) else 1


def _line(case_id: str, ok: bool, detail: str) -> str:
    mark = "PASS" if ok else "FAIL"
    return f"[{mark}] {case_id}: {detail}"


if __name__ == "__main__":
    raise SystemExit(main())
