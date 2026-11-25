"""Stockage SQLite des élèves."""
from dataclasses import asdict

from sqlalchemy import delete

from ....domain.entities import Eleve
from ..modeles import EleveModele
from .base import SqlRepository, valider


class SqlEleveRepository(SqlRepository[Eleve]):
    modele = EleveModele
    entite = Eleve

    def ajouter_plusieurs(self, eleves: list[Eleve]) -> list[Eleve]:
        with self._sessions() as s:
            s.add_all(EleveModele(**asdict(e)) for e in eleves)
            valider(s)
        return eleves

    def supprimer_par_classe(self, classe_id: str) -> int:
        with self._sessions() as s:
            n = s.execute(delete(EleveModele).where(EleveModele.classe_id == classe_id)).rowcount
            valider(s)
            return n
