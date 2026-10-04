"""Prueba arquitectónica: el dominio no depende de librerías externas (§2.4, §5.17).

Verifica por AST que ningún módulo de ``app/domain`` importe frameworks,
SDKs ni otras capas del proyecto. Es la garantía ejecutable de la Regla
de Oro (§2.13).
"""

import ast
from pathlib import Path

import pytest

DOMAIN_PATH = Path(__file__).resolve().parents[2] / "app" / "domain"

ALLOWED_TOP_LEVEL = {
    # stdlib utilizada por el dominio
    "abc",
    "collections",
    "dataclasses",
    "datetime",
    "enum",
    "pathlib",
    "typing",
    # el dominio puede importarse a sí mismo
    "app",
}

FORBIDDEN_APP_PREFIXES = (
    "app.application",
    "app.presentation",
    "app.infrastructure",
    "app.config",
)


def _imports_of(file: Path) -> list[str]:
    tree = ast.parse(file.read_text(encoding="utf-8"))
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return names


@pytest.mark.unit
def test_domain_has_no_external_dependencies() -> None:
    violations: list[str] = []
    for file in DOMAIN_PATH.rglob("*.py"):
        for module in _imports_of(file):
            top = module.split(".")[0]
            if top not in ALLOWED_TOP_LEVEL:
                violations.append(f"{file.name}: import externo '{module}'")
            if module.startswith(FORBIDDEN_APP_PREFIXES):
                violations.append(f"{file.name}: importa otra capa '{module}'")
            if top == "app" and not module.startswith("app.domain"):
                violations.append(f"{file.name}: import fuera del dominio '{module}'")
    assert not violations, "El dominio viola su pureza:\n" + "\n".join(violations)
