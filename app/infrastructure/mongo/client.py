"""Connexion MongoDB — sans effet de bord à l'import (pymongo se connecte à la première requête)."""
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import PyMongoError


def creer_client(uri: str) -> MongoClient:
    # minPoolSize : connexions gardées ouvertes (ouvrir une connexion TLS vers Atlas coûte ~0,5 s),
    # assez pour lire toutes les collections en parallèle (voir emploi_du_temps_repository.charger)
    return MongoClient(uri, serverSelectionTimeoutMS=5000, tz_aware=False, minPoolSize=8)


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
