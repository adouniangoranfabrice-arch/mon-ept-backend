"""Stockage MongoDB des entités Jour (collection « jours »)."""
from ....domain.entities import Jour
from .base import MongoRepository


class MongoJourRepository(MongoRepository[Jour]):
    collection = "jours"
    entite = Jour
