"""Stockage SQLite des entités Heure."""
from ....domain.entities import Heure
from ..modeles import HeureModele
from .base import SqlRepository


class SqlHeureRepository(SqlRepository[Heure]):
    modele = HeureModele
    entite = Heure
