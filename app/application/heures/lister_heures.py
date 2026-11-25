"""Lister les créneaux horaires."""
from ..commun.crud import ListerElements


class ListerHeures(ListerElements):
    table = "heures"
