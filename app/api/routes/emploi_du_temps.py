"""Routes sur l'ensemble des données : lecture, import d'une sauvegarde, réinitialisation."""
from fastapi import APIRouter

from ...application.emploi_du_temps.importer_emploi_du_temps import ImporterEmploiDuTemps
from ...application.emploi_du_temps.lire_emploi_du_temps import LireEmploiDuTemps
from ...application.emploi_du_temps.reinitialiser_emploi_du_temps import ReinitialiserEmploiDuTemps
from ..dependencies import cas_usage
from ..schemas.emploi_du_temps import EmploiDuTempsIn, EmploiDuTempsOut

router = APIRouter(tags=["emploi du temps"])


@router.get("/data", response_model=EmploiDuTempsOut, summary="Toutes les données")
def lire(cas: LireEmploiDuTemps = cas_usage(LireEmploiDuTemps)):
    return cas.executer()


@router.put("/data", response_model=EmploiDuTempsOut, summary="Remplacer toutes les données (import)")
def importer(payload: EmploiDuTempsIn, cas: ImporterEmploiDuTemps = cas_usage(ImporterEmploiDuTemps)):
    return cas.executer(payload.model_dump())


@router.post("/reset", response_model=EmploiDuTempsOut, summary="Revenir aux données de départ")
def reinitialiser(cas: ReinitialiserEmploiDuTemps = cas_usage(ReinitialiserEmploiDuTemps)):
    return cas.executer()
