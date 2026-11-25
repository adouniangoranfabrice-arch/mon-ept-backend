"""Stockage MongoDB des séances (collection « seances »)."""
from ....domain.entities import Seance
from .base import MongoRepository


class MongoSeanceRepository(MongoRepository[Seance]):
    collection = "seances"
    entite = Seance

    def supprimer_liees(self, champ: str, id: str) -> int:
        return self._col.delete_many({champ: id}).deleted_count
