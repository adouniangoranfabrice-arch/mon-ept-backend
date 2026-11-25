from pydantic import BaseModel, ConfigDict


class Entree(BaseModel):
    """Base des DTO d'entrée : champs inconnus ignorés, espaces retirés."""

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)
    id: str | None = None


class Sortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class SuppressionOut(Sortie):
    id: str
    seances_supprimees: int
    eleves_supprimes: int = 0
    evaluations_supprimees: int = 0
    notes_supprimees: int = 0
