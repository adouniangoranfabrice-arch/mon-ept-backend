"""Créer une séance — règles : jour, heure et classe existants ; un seul cours par créneau."""
from ..commun.crud import CreerElement


class CreerSeance(CreerElement):
    table = "seances"
