"""Supprimer le jour et ses séances."""
from ..commun.crud import SupprimerElement


class SupprimerJour(SupprimerElement):
    table = "jours"
