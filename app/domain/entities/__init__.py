"""Entités métier (dataclasses)."""
from .classe import Classe
from .eleve import Eleve
from .evaluation import TRIMESTRES, Evaluation
from .emploi_du_temps import ENTITES, LIEN_SEANCE, NOMS, TABLES, EmploiDuTemps, Entite, depuis_dict
from .heure import Heure
from .jour import Jour
from .note import Note, moyenne, moyenne_annuelle
from .seance import Seance

__all__ = [
    "Classe", "Eleve", "EmploiDuTemps", "Entite", "Evaluation", "Heure", "Jour", "Note", "Seance",
    "TRIMESTRES", "moyenne", "moyenne_annuelle",
    "ENTITES", "LIEN_SEANCE", "NOMS", "TABLES", "depuis_dict",
]
