"""Stockage SQLite des entités Jour."""
from ....domain.entities import Jour
from ..modeles import JourModele
from .base import SqlRepository


class SqlJourRepository(SqlRepository[Jour]):
    modele = JourModele
    entite = Jour
