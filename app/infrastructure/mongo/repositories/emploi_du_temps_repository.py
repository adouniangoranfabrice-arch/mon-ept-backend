"""Lecture globale et remplacement complet (import) de l'emploi du temps."""
from concurrent.futures import ThreadPoolExecutor

from pymongo.database import Database

from ....domain.entities import ENTITES, TABLES, EmploiDuTemps
from ..client import supporte_transactions
from .base import vers_document, vers_entite

# Partagé par toutes les requêtes (pymongo est thread-safe) : une lecture par collection
_POOL = ThreadPoolExecutor(max_workers=len(TABLES), thread_name_prefix="mongo-charger")


class MongoEmploiDuTempsRepository:
    def __init__(self, db: Database):
        self._db = db

    def charger(self, notes: bool = False) -> EmploiDuTemps:
        """Les collections sont lues en parallèle : le temps total ≈ une seule requête
        au lieu de la somme (chaque aller-retour vers Atlas coûte ~100-200 ms)."""
        tables = [t for t in TABLES if notes or t != "notes"]
        # batch_size élevé : tout arrive en un seul aller-retour (sinon pymongo coupe à 101 documents)
        lire = lambda t: [vers_entite(ENTITES[t], d) for d in self._db[t].find(batch_size=10_000)]
        return EmploiDuTemps(**dict(zip(tables, _POOL.map(lire, tables))))

    def remplacer_tout(self, edt: EmploiDuTemps) -> None:
        if supporte_transactions(self._db):  # Atlas / replica set : tout ou rien
            with self._db.client.start_session() as session:
                session.with_transaction(lambda s: self._remplacer(edt, s))
        else:  # serveur seul : les données sont déjà entièrement validées avant
            self._remplacer(edt, None)

    def _remplacer(self, edt: EmploiDuTemps, session) -> None:
        for t in reversed(TABLES):
            self._db[t].delete_many({}, session=session)
        for t in TABLES:
            if docs := [vers_document(e) for e in edt.liste(t)]:
                self._db[t].insert_many(docs, session=session)
