"""Créer une évaluation (interrogation, devoir…) pour une classe et un trimestre."""
from ..commun.crud import CreerElement


class CreerEvaluation(CreerElement):
    table = "evaluations"
