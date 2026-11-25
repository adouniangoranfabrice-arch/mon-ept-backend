"""Lister les jours."""
from ..commun.crud import ListerElements


class ListerJours(ListerElements):
    table = "jours"
