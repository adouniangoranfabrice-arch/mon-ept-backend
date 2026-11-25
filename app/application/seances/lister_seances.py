"""Lister les séances (par jour puis par heure)."""
from ..commun.crud import ListerElements


class ListerSeances(ListerElements):
    table = "seances"
