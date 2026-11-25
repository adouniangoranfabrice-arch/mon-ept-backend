"""Modifier le créneau — mêmes règles qu'à la création."""
from ..commun.crud import ModifierElement


class ModifierHeure(ModifierElement):
    table = "heures"
