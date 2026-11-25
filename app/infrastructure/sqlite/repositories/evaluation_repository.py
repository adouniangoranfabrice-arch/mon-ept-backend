"""Stockage SQLite des évaluations."""
from sqlalchemy import delete

from ....domain.entities import Evaluation
from ..modeles import EvaluationModele
from .base import SqlRepository, valider


class SqlEvaluationRepository(SqlRepository[Evaluation]):
    modele = EvaluationModele
    entite = Evaluation

    def supprimer_par_classe(self, classe_id: str) -> int:
        with self._sessions() as s:
            n = s.execute(delete(EvaluationModele).where(EvaluationModele.classe_id == classe_id)).rowcount
            valider(s)
            return n
