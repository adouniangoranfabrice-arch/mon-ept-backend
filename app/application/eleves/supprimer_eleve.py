"""Supprimer un élève."""
from ..commun.crud import SupprimerElement


class SupprimerEleve(SupprimerElement):
    table = "eleves"
