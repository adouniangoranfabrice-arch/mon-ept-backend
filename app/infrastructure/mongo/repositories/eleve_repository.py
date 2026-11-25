"""Stockage MongoDB des élèves (collection « eleves »)."""
from ....domain.entities import Eleve
from .base import MongoRepository, vers_document


class MongoEleveRepository(MongoRepository[Eleve]):
    collection = "eleves"
    entite = Eleve

    def ajouter_plusieurs(self, eleves: list[Eleve]) -> list[Eleve]:
        if eleves:
            self._col.insert_many([vers_document(e) for e in eleves])
        return eleves

    def supprimer_par_classe(self, classe_id: str) -> int:
        return self._col.delete_many({"classe_id": classe_id}).deleted_count
