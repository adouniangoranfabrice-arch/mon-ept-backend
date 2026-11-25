"""Stockage SQLite des séances."""
from sqlalchemy import delete

from ....domain.entities import Seance
from ..modeles import SeanceModele
from .base import SqlRepository, valider


class SqlSeanceRepository(SqlRepository[Seance]):
    modele = SeanceModele
    entite = Seance

    def supprimer_liees(self, champ: str, id: str) -> int:
        with self._sessions() as s:
            n = s.execute(delete(SeanceModele).where(getattr(SeanceModele, champ) == id)).rowcount
            valider(s)
            return n
