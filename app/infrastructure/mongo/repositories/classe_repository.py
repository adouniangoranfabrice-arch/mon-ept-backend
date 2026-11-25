"""Stockage MongoDB des entités Classe (collection « classes »)."""
from ....domain.entities import Classe
from .base import MongoRepository


class MongoClasseRepository(MongoRepository[Classe]):
    collection = "classes"
    entite = Classe
