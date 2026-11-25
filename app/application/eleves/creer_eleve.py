"""Ajouter un élève dans une classe — règles : nom obligatoire, pas de doublon dans la classe."""
from ..commun.crud import CreerElement


class CreerEleve(CreerElement):
    table = "eleves"
