"""Voir une séance."""
from ..commun.crud import VoirElement


class VoirSeance(VoirElement):
    table = "seances"
