"""Repository SQLite générique : conversions entité ↔ modèle et opérations communes."""
from dataclasses import asdict
from typing import ClassVar, Generic, TypeVar

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from ....domain.errors import Conflit

T = TypeVar("T")
MESSAGE_CONFLIT = "Conflit avec des données existantes (créneau déjà pris ?)."


def vers_entite(entite_cls: type, obj):
    return entite_cls(**{c.name: getattr(obj, c.name) for c in obj.__table__.columns})


def valider(session: Session) -> None:
    """Commit ; une violation de contrainte devient une erreur du domaine."""
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise Conflit(MESSAGE_CONFLIT) from None


class SqlRepository(Generic[T]):
    modele: ClassVar[type]
    entite: ClassVar[type]

    def __init__(self, sessions: sessionmaker):
        self._sessions = sessions

    def obtenir(self, id: str) -> T | None:
        with self._sessions() as s:
            obj = s.get(self.modele, id)
            return vers_entite(self.entite, obj) if obj else None

    def ajouter(self, entite: T) -> T:
        with self._sessions() as s:
            s.add(self.modele(**asdict(entite)))
            valider(s)
        return entite

    def modifier(self, entite: T) -> T:
        with self._sessions() as s:
            obj = s.get(self.modele, entite.id)
            for k, v in asdict(entite).items():
                setattr(obj, k, v)
            valider(s)
        return entite

    def supprimer(self, id: str) -> None:
        with self._sessions() as s:
            if obj := s.get(self.modele, id):
                s.delete(obj)
            valider(s)
