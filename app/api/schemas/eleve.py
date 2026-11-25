from pydantic import BaseModel, Field

from .commun import Entree, Sortie


class EleveIn(Entree):
    nom_prenoms: str = ""
    classe_id: str = ""


class EleveOut(Sortie):
    id: str
    nom_prenoms: str
    classe_id: str


class ApercuFichierOut(Sortie):
    """Résultat de la lecture du fichier Excel, avant import."""

    noms: list[str]
    doublons_fichier: int


class ImportElevesIn(BaseModel):
    classe_id: str
    noms: list[str] = Field(max_length=2000)


class ImportElevesOut(Sortie):
    ajoutes: list[EleveOut]
    ignores: list[str]
