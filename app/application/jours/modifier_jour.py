"""Modifier le jour — mêmes règles qu'à la création."""
from ..commun.crud import ModifierElement


class ModifierJour(ModifierElement):
    table = "jours"
