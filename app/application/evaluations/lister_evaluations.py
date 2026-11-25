"""Lister les évaluations (par classe, trimestre puis date)."""
from ..commun.crud import ListerElements


class ListerEvaluations(ListerElements):
    table = "evaluations"
