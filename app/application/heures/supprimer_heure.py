"""Supprimer le créneau et ses séances."""
from ..commun.crud import SupprimerElement


class SupprimerHeure(SupprimerElement):
    table = "heures"
