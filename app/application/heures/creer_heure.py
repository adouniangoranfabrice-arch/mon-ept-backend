"""Créer un créneau horaire — règles : code unique, fin après le début, sans chevauchement."""
from ..commun.crud import CreerElement


class CreerHeure(CreerElement):
    table = "heures"
