"""Voir un créneau horaire."""
from ..commun.crud import VoirElement


class VoirHeure(VoirElement):
    table = "heures"
