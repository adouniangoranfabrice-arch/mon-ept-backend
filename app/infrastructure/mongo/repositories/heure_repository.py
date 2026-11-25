"""Stockage MongoDB des entités Heure (collection « heures »)."""
from ....domain.entities import Heure
from .base import MongoRepository


class MongoHeureRepository(MongoRepository[Heure]):
    collection = "heures"
    entite = Heure
