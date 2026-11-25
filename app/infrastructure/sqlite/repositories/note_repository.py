"""Stockage SQLite des notes."""
from dataclasses import asdict

from sqlalchemy import delete, select
from sqlalchemy.orm import sessionmaker

from ....domain.entities import Note
from ..modeles import NoteModele
from .base import valider, vers_entite


class SqlNoteRepository:
    def __init__(self, sessions: sessionmaker):
        self._sessions = sessions

    def lister_par_evaluation(self, evaluation_id: str) -> list[Note]:
        with self._sessions() as s:
            requete = select(NoteModele).where(NoteModele.evaluation_id == evaluation_id)
            return [vers_entite(Note, o) for o in s.scalars(requete)]

    def remplacer_pour_evaluation(self, evaluation_id: str, notes: list[Note]) -> None:
        with self._sessions() as s:  # une seule transaction
            s.execute(delete(NoteModele).where(NoteModele.evaluation_id == evaluation_id))
            s.add_all(NoteModele(**asdict(n)) for n in notes)
            valider(s)

    def supprimer_par_evaluations(self, evaluation_ids: list[str]) -> int:
        if not evaluation_ids:
            return 0
        with self._sessions() as s:
            n = s.execute(delete(NoteModele).where(NoteModele.evaluation_id.in_(evaluation_ids))).rowcount
            valider(s)
            return n

    def supprimer_par_eleves(self, eleve_ids: list[str]) -> int:
        if not eleve_ids:
            return 0
        with self._sessions() as s:
            n = s.execute(delete(NoteModele).where(NoteModele.eleve_id.in_(eleve_ids))).rowcount
            valider(s)
            return n
