"""Lister les classes (de la 6e à la Tle)."""
from ..commun.crud import ListerElements


class ListerClasses(ListerElements):
    table = "classes"
