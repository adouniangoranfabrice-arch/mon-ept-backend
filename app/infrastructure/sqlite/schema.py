"""Création des tables, appelée au démarrage (équivalent de create_indexes())."""
from pathlib import Path

from sqlalchemy import Engine

from .modeles import Base


def creer_schema(moteur: Engine, chemin: Path) -> bool:
    """Crée les tables manquantes. Renvoie True si la base vient d'être créée (à remplir)."""
    neuve = not chemin.exists()
    Base.metadata.create_all(moteur)
    return neuve
