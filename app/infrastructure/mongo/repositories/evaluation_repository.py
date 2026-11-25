"""Stockage MongoDB des évaluations (collection « evaluations »)."""
from ....domain.entities import Evaluation
from .base import MongoRepository


class MongoEvaluationRepository(MongoRepository[Evaluation]):
    collection = "evaluations"
    entite = Evaluation

    def supprimer_par_classe(self, classe_id: str) -> int:
        return self._col.delete_many({"classe_id": classe_id}).deleted_count
