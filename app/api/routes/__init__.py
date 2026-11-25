"""Regroupe toutes les routes sous /api."""
from fastapi import APIRouter

from . import classes, eleves, emploi_du_temps, evaluations, heures, jours, seances, systeme


def creer_routeur_api() -> APIRouter:
    api = APIRouter(prefix="/api")
    for module in (systeme, emploi_du_temps, jours, heures, classes, eleves, evaluations, seances):
        api.include_router(module.router)
    return api
