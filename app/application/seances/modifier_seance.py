"""Modifier la séance — mêmes règles qu'à la création."""
from ..commun.crud import ModifierElement


class ModifierSeance(ModifierElement):
    table = "seances"
