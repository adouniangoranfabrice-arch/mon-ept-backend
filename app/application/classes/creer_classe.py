"""Créer une classe — règles : nom unique, effectif positif, couleur obligatoire."""
from ..commun.crud import CreerElement


class CreerClasse(CreerElement):
    table = "classes"
