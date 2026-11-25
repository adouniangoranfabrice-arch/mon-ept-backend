"""Choix du stockage (MongoDB ou SQLite) selon les Settings — utilisé par main.py et scripts/."""
from dataclasses import dataclass
from typing import Callable

from ..config import Settings
from ..domain.ports.repositories import Depots


@dataclass
class Stockage:
    nom: str  # "mongodb" ou "sqlite"
    depots: Depots
    preparer: Callable[[], bool]  # crée tables/index ; True si la base est vide (à remplir)
    description: str


def ouvrir_stockage(settings: Settings, client_mongo=None) -> Stockage:
    """`client_mongo` permet aux tests de fournir un faux client (mongomock)."""
    if settings.stockage == "mongodb":
        from .mongo.client import creer_client, verifier_connexion
        from .mongo.fabrique import creer_depots_mongo
        from .mongo.indexes import create_indexes

        if client_mongo is None and not settings.mongodb_uri:
            raise RuntimeError("EDT_STOCKAGE=mongodb mais MONGODB_URI n'est pas défini (backend/.env).")
        client = client_mongo or creer_client(settings.mongodb_uri)
        db = client[settings.mongodb_db]

        def preparer() -> bool:
            if client_mongo is None:
                verifier_connexion(db)
            return create_indexes(db)

        return Stockage("mongodb", creer_depots_mongo(db), preparer, f"MongoDB, base « {settings.mongodb_db} »")

    from .sqlite.fabrique import creer_depots_sqlite
    from .sqlite.schema import creer_schema

    moteur, depots = creer_depots_sqlite(settings.db_path)
    return Stockage("sqlite", depots, lambda: creer_schema(moteur, settings.db_path), f"SQLite, {settings.db_path}")
