"""Routes /api/jours — chaque route appelle un seul cas d'usage."""
from fastapi import APIRouter

from ...application.jours.creer_jour import CreerJour
from ...application.jours.lister_jours import ListerJours
from ...application.jours.modifier_jour import ModifierJour
from ...application.jours.supprimer_jour import SupprimerJour
from ...application.jours.voir_jour import VoirJour
from ..dependencies import cas_usage
from ..schemas.commun import SuppressionOut
from ..schemas.jour import JourIn, JourOut

router = APIRouter(prefix="/jours", tags=["jours"])


@router.get("", response_model=list[JourOut], summary="Lister les jours (lundi → dimanche)")
def lister(cas: ListerJours = cas_usage(ListerJours)):
    return cas.executer()


@router.get("/{id}", response_model=JourOut, summary="Voir un jour")
def voir(id: str, cas: VoirJour = cas_usage(VoirJour)):
    return cas.executer(id)


@router.post("", status_code=201, response_model=JourOut, summary="Créer un jour")
def creer(payload: JourIn, cas: CreerJour = cas_usage(CreerJour)):
    return cas.executer(payload.model_dump())


@router.put("/{id}", response_model=JourOut, summary="Modifier un jour")
def modifier(id: str, payload: JourIn, cas: ModifierJour = cas_usage(ModifierJour)):
    return cas.executer(id, payload.model_dump())


@router.delete("/{id}", response_model=SuppressionOut, summary="Supprimer le jour et ses séances")
def supprimer(id: str, cas: SupprimerJour = cas_usage(SupprimerJour)):
    return cas.executer(id)
