"""Supprimer une évaluation et toutes ses notes."""
from ..commun.crud import SupprimerElement


class SupprimerEvaluation(SupprimerElement):
    table = "evaluations"
