from pydantic import BaseModel, Field

from .commun import Entree, Sortie


class EvaluationIn(Entree):
    classe_id: str = ""
    trimestre: int
    libelle: str = ""
    date: str | None = ""
    bareme: float = 20
    coefficient: float = 1


class EvaluationOut(Sortie):
    id: str
    classe_id: str
    trimestre: int
    libelle: str
    date: str
    bareme: float
    coefficient: float


class NoteIn(Entree):
    """Note complète (import d'une sauvegarde)."""

    evaluation_id: str = ""
    eleve_id: str = ""
    valeur: float


class NoteOut(Sortie):
    id: str
    evaluation_id: str
    eleve_id: str
    valeur: float


class SaisieNote(BaseModel):
    eleve_id: str
    valeur: float | None = None  # vide = pas de note (absent, non noté)


class SaisieNotesIn(BaseModel):
    notes: list[SaisieNote] = Field(max_length=500)
