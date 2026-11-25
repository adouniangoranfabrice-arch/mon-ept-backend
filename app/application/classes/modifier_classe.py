"""Modifier la classe — mêmes règles qu'à la création."""
from ..commun.crud import ModifierElement


class ModifierClasse(ModifierElement):
    table = "classes"
