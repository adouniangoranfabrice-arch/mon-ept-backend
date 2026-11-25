"""Créer un jour — règles : libellé et ordre (1 à 7) uniques."""
from ..commun.crud import CreerElement


class CreerJour(CreerElement):
    table = "jours"
