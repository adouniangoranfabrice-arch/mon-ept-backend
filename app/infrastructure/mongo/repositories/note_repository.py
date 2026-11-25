"""Stockage MongoDB des notes (collection « notes »)."""
from pymongo.database import Database

from ....domain.entities import Note
from ..client import supporte_transactions
from .base import vers_document, vers_entite


class MongoNoteRepository:
    def __init__(self, db: Database):
        self._db = db
        self._col = db.notes

    def lister_par_evaluation(self, evaluation_id: str) -> list[Note]:
        return [vers_entite(Note, d) for d in self._col.find({"evaluation_id": evaluation_id})]

    def remplacer_pour_evaluation(self, evaluation_id: str, notes: list[Note]) -> None:
        def remplacer(session=None):
            self._col.delete_many({"evaluation_id": evaluation_id}, session=session)
            if notes:
                self._col.insert_many([vers_document(n) for n in notes], session=session)

        if supporte_transactions(self._db):  # Atlas : tout ou rien
            with self._db.client.start_session() as session:
                session.with_transaction(lambda s: remplacer(s))
        else:
            remplacer()

    def supprimer_par_evaluations(self, evaluation_ids: list[str]) -> int:
        if not evaluation_ids:
            return 0
        return self._col.delete_many({"evaluation_id": {"$in": evaluation_ids}}).deleted_count

    def supprimer_par_eleves(self, eleve_ids: list[str]) -> int:
        if not eleve_ids:
            return 0
        return self._col.delete_many({"eleve_id": {"$in": eleve_ids}}).deleted_count
