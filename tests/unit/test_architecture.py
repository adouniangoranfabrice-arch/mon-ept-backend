"""Vérifie la règle des dépendances : elles pointent toujours vers le domaine.

domain          → rien d'extérieur (aucun framework, aucune autre couche)
application     → domain uniquement
infrastructure  → domain (jamais api, ni FastAPI/Pydantic)
api             → application + domain (jamais infrastructure, ni SQLAlchemy)
"""
import ast
from pathlib import Path

import pytest

APP = Path(__file__).resolve().parents[2] / "app"
FRAMEWORKS = {"fastapi", "starlette", "sqlalchemy", "pydantic", "uvicorn"}

INTERDITS = {
    "domain": FRAMEWORKS | {"application", "infrastructure", "api", "main", "config"},
    "application": FRAMEWORKS | {"infrastructure", "api", "main", "config"},
    "infrastructure": {"fastapi", "starlette", "pydantic", "api", "main"},
    "api": {"sqlalchemy", "infrastructure", "main"},
}


def _imports(fichier: Path) -> set[str]:
    """Bibliothèques et couches importées (« from ...domain.x » → domain ; « from .x » ignoré)."""
    couche = fichier.relative_to(APP).parts[0]
    profondeur = len(fichier.relative_to(APP).parts) - 1  # nombre de dossiers sous app/
    noms = set()
    for noeud in ast.walk(ast.parse(fichier.read_text(encoding="utf-8"))):
        if isinstance(noeud, ast.Import):
            noms |= {a.name.split(".")[0] for a in noeud.names}
        elif isinstance(noeud, ast.ImportFrom):
            if noeud.level == 0:
                parts = (noeud.module or "").split(".")
                noms.add(parts[1] if parts[0] == "app" and len(parts) > 1 else parts[0])
            elif noeud.level > profondeur and noeud.module:
                noms.add(noeud.module.split(".")[0])  # remonte jusqu'à app/ : vise une autre couche
            else:
                noms.add(couche)  # reste dans la même couche
    return noms - {couche}


@pytest.mark.parametrize("couche", list(INTERDITS))
def test_regle_des_dependances(couche):
    fichiers = list((APP / couche).rglob("*.py"))
    assert fichiers, f"Couche {couche} introuvable"
    for fichier in fichiers:
        interdits = _imports(fichier) & INTERDITS[couche]
        assert not interdits, f"{fichier.relative_to(APP)} importe {interdits}"


def test_detecte_une_violation():
    """Le test ci-dessus sait-il vraiment repérer un import interdit ?"""
    piege = APP / "domain" / "entities" / "_piege_test.py"
    piege.write_text("from ...infrastructure.sqlite import client\nimport sqlalchemy\n", encoding="utf-8")
    try:
        assert _imports(piege) & INTERDITS["domain"] == {"infrastructure", "sqlalchemy"}
    finally:
        piege.unlink()
