from pydantic import field_validator

from .commun import Entree, Sortie


class ClasseIn(Entree):
    nom: str = ""
    niveau: str | None = ""
    effectif: int | None = None
    couleur: str = ""

    @field_validator("effectif", mode="before")
    @classmethod
    def _vide_vers_none(cls, v):
        return None if v == "" else v


class ClasseOut(Sortie):
    id: str
    nom: str
    niveau: str
    effectif: int | None
    couleur: str
