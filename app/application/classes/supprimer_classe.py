"""Supprimer la classe et ses séances."""
from ..commun.crud import SupprimerElement


class SupprimerClasse(SupprimerElement):
    table = "classes"
