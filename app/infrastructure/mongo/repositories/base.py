"""Repository MongoDB générique : un document par entité, l'id de l'entité sert de _id."""
from dataclasses import asdict
from typing import ClassVar, Generic, TypeVar

from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from ....domain.errors import Conflit

T = TypeVar("T")
MESSAGE_CONFLIT = "Conflit avec des données existantes (créneau déjà pris ?)."


def vers_document(entite) -> dict:
    doc = asdict(entite)
    doc["_id"] = doc.pop("id")
    return doc


def vers_entite(entite_cls: type, doc: dict):
    doc = dict(doc)
    doc["id"] = doc.pop("_id")
    return entite_cls(**doc)


class MongoRepository(Generic[T]):
    collection: ClassVar[str]
    entite: ClassVar[type]

    def __init__(self, db: Database):
        self._col = db[self.collection]

    def obtenir(self, id: str) -> T | None:
        doc = self._col.find_one({"_id": id})
        return vers_entite(self.entite, doc) if doc else None

    def ajouter(self, entite: T) -> T:
        try:
            self._col.insert_one(vers_document(entite))
        except DuplicateKeyError:
            raise Conflit(MESSAGE_CONFLIT) from None
        return entite

    def modifier(self, entite: T) -> T:
        try:
            self._col.replace_one({"_id": entite.id}, vers_document(entite))
        except DuplicateKeyError:
            raise Conflit(MESSAGE_CONFLIT) from None
        return entite

    def supprimer(self, id: str) -> None:
        self._col.delete_one({"_id": id})
