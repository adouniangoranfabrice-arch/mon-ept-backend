"""Connexion MongoDB — sans effet de bord à l'import (pymongo se connecte à la première requête)."""
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import PyMongoError


def creer_client(uri: str) -> MongoClient:
    return MongoClient(uri, serverSelectionTimeoutMS=5000, tz_aware=False)


def verifier_connexion(db: Database) -> None:
    """Échoue tout de suite, avec un message clair, si MongoDB est injoignable."""
    try:
        db.client.admin.command("ping")
    except PyMongoError as e:
        raise RuntimeError(
            "Impossible de joindre MongoDB. Vérifiez MONGODB_URI dans backend/.env "
            f"et que le serveur (ou le cluster Atlas) est accessible. Détail : {e}"
        ) from e


def supporte_transactions(db: Database) -> bool:
    """Les transactions demandent un replica set (toujours le cas sur Atlas)."""
    description = getattr(db.client, "topology_description", None)
    return getattr(description, "topology_type_name", "") in ("ReplicaSetWithPrimary", "Sharded", "LoadBalanced")
