"""Lister les élèves (par classe de la 6e à la Tle, puis par ordre alphabétique)."""
from ..commun.crud import ListerElements


class ListerEleves(ListerElements):
    table = "eleves"
