"""Settings : configuration lue dans l'environnement et dans backend/.env."""
import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]


def _lire_env(fichier: Path) -> dict[str, str]:
    """Lit un fichier .env simple (CLE=valeur, lignes # ignorées)."""
    if not fichier.is_file():
        return {}
    valeurs = {}
    for ligne in fichier.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if ligne and not ligne.startswith("#") and "=" in ligne:
            cle, valeur = ligne.split("=", 1)
            valeurs[cle.strip()] = valeur.strip().strip('"').strip("'")
    return valeurs


def _env(cle: str, defaut: str = "") -> str:
    """Variable d'environnement, sinon valeur de backend/.env, sinon défaut."""
    return os.environ.get(cle) or _lire_env(BACKEND_DIR / ".env").get(cle) or defaut


@dataclass(frozen=True)
class Settings:
    # MongoDB : si MONGODB_URI est défini, c'est le stockage utilisé
    mongodb_uri: str = field(default_factory=lambda: _env("MONGODB_URI"))
    mongodb_db: str = field(default_factory=lambda: _env("MONGODB_DB", "emploi_du_temps"))
    # SQLite (stockage par défaut sans MongoDB) : backend/edt.db
    db_path: Path = field(default_factory=lambda: Path(_env("EDT_DB_PATH", str(BACKEND_DIR / "edt.db"))))
    # Forcer un stockage : "mongodb" ou "sqlite" (sinon déduit de MONGODB_URI)
    stockage_force: str = field(default_factory=lambda: _env("EDT_STOCKAGE").lower())
    # Frontend compilé (npm run build), servi par le backend s'il existe
    dist_dir: Path = field(default_factory=lambda: Path(_env("EDT_DIST_DIR", str(BACKEND_DIR.parent / "frontend" / "dist"))))
    cors_origins: tuple[str, ...] = ("http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:4173")

    @property
    def stockage(self) -> str:
        if self.stockage_force in ("mongodb", "sqlite"):
            return self.stockage_force
        return "mongodb" if self.mongodb_uri else "sqlite"


@lru_cache
def get_settings() -> Settings:
    return Settings()
