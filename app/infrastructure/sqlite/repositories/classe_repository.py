"""Stockage SQLite des entités Classe."""
from ....domain.entities import Classe
from ..modeles import ClasseModele
from .base import SqlRepository


class SqlClasseRepository(SqlRepository[Classe]):
    modele = ClasseModele
    entite = Classe
