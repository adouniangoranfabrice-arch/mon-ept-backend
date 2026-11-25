from pydantic import BaseModel, ConfigDict

from .classe import ClasseIn, ClasseOut
from .commun import Sortie
from .eleve import EleveIn, EleveOut
from .evaluation import EvaluationIn, EvaluationOut, NoteIn, NoteOut
from .heure import HeureIn, HeureOut
from .jour import JourIn, JourOut
from .seance import SeanceIn, SeanceOut


class EmploiDuTempsIn(BaseModel):
    """Sauvegarde complète à importer."""

    model_config = ConfigDict(extra="ignore")
    jours: list[JourIn]
    heures: list[HeureIn]
    classes: list[ClasseIn]
    eleves: list[EleveIn] = []  # absents des anciennes sauvegardes
    evaluations: list[EvaluationIn] = []
    notes: list[NoteIn] = []
    seances: list[SeanceIn]


class EmploiDuTempsOut(Sortie):
    jours: list[JourOut]
    heures: list[HeureOut]
    classes: list[ClasseOut]
    eleves: list[EleveOut]
    evaluations: list[EvaluationOut]
    notes: list[NoteOut]
    seances: list[SeanceOut]
