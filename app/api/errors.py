"""Erreurs du domaine traduites en HTTP : ErreurValidation → 400, Introuvable → 404, Conflit → 409."""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from ..domain.errors import Conflit, ErreurDomaine, ErreurValidation, Introuvable

CODES = {ErreurValidation: 400, Introuvable: 404, Conflit: 409}

LIBELLES = {
    "libelle": "Libellé", "ordre": "Ordre", "actif": "Actif", "code": "Code",
    "heure_debut": "Début", "heure_fin": "Fin", "nom": "Nom", "niveau": "Niveau",
    "effectif": "Effectif", "couleur": "Couleur", "jour_id": "Jour", "heure_id": "Heure",
    "classe_id": "Classe", "salle": "Salle", "recurrente": "Récurrente",
    "nom_prenoms": "Nom et prénoms", "noms": "Liste des élèves", "fichier": "Fichier",
    "trimestre": "Trimestre", "date": "Date", "bareme": "Barème", "coefficient": "Coefficient",
    "valeur": "Note", "evaluation_id": "Évaluation", "eleve_id": "Élève",
}


async def _erreur_domaine(_req: Request, exc: ErreurDomaine):
    return JSONResponse(status_code=CODES.get(type(exc), 400), content={"detail": exc.message})


async def _erreur_format(_req: Request, exc: RequestValidationError):
    """Erreurs de format (ex. effectif = « abc ») → message en français (422)."""
    err = exc.errors()[0] if exc.errors() else {}
    champs = [str(x) for x in err.get("loc", ()) if x != "body"]
    if champs:
        detail = f"Valeur invalide pour « {LIBELLES.get(champs[-1], champs[-1])} »."
        if len(champs) > 1:
            detail += f" (emplacement : {' › '.join(champs)})"
    else:
        detail = "Données manquantes ou invalides."
    return JSONResponse(status_code=422, content={"detail": detail})


def installer_gestionnaires_erreurs(app: FastAPI) -> None:
    app.add_exception_handler(ErreurDomaine, _erreur_domaine)
    app.add_exception_handler(RequestValidationError, _erreur_format)
