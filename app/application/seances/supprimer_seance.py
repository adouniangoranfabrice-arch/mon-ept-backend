"""Supprimer la séance."""
from ..commun.crud import SupprimerElement


class SupprimerSeance(SupprimerElement):
    table = "seances"
