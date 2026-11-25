"""Lecture globale et remplacement complet (import) de l'emploi du temps."""
from pymongo.database import Database

from ....domain.entities import ENTITES, TABLES, EmploiDuTemps
from ..client import supporte_transactions
from .base import vers_document, vers_entite


class MongoEmploiDuTempsRepository:
    def __init__(self, db: Database):
        self._db = db

    def charger(self, notes: bool = False) -> EmploiDuTemps:
        tables = [t for t in TABLES if notes or t != "notes"]
        return EmploiDuTemps(**{t: [vers_entite(ENTITES[t], d) for d in self._db[t].find()] for t in tables})

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
