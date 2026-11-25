"""Voir une évaluation."""
from ..commun.crud import VoirElement


class VoirEvaluation(VoirElement):
    table = "evaluations"
