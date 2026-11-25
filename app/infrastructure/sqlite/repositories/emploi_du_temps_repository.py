"""Lecture globale et remplacement complet (import) de l'emploi du temps."""
from dataclasses import asdict

from sqlalchemy import delete, select
from sqlalchemy.orm import sessionmaker

from ....domain.entities import ENTITES, TABLES, EmploiDuTemps
from ..modeles import MODELES
from .base import valider, vers_entite


class SqlEmploiDuTempsRepository:
    def __init__(self, sessions: sessionmaker):
        self._sessions = sessions

    def charger(self, notes: bool = False) -> EmploiDuTemps:
        tables = [t for t in TABLES if notes or t != "notes"]
        with self._sessions() as s:
            return EmploiDuTemps(
                **{t: [vers_entite(ENTITES[t], o) for o in s.scalars(select(MODELES[t]))] for t in tables}
            )

    def remplacer_tout(self, edt: EmploiDuTemps) -> None:
        with self._sessions() as s:  # une seule transaction : tout ou rien
            for t in reversed(TABLES):
                s.execute(delete(MODELES[t]))
            for t in TABLES:
                s.add_all(MODELES[t](**asdict(e)) for e in edt.liste(t))
            valider(s)
