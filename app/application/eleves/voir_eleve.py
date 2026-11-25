"""Voir un élève."""
from ..commun.crud import VoirElement


class VoirEleve(VoirElement):
    table = "eleves"
