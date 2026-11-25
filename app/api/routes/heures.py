"""Routes /api/heures — chaque route appelle un seul cas d'usage."""
from fastapi import APIRouter

from ...application.heures.creer_heure import CreerHeure
from ...application.heures.lister_heures import ListerHeures
from ...application.heures.modifier_heure import ModifierHeure
from ...application.heures.supprimer_heure import SupprimerHeure
from ...application.heures.voir_heure import VoirHeure
from ..dependencies import cas_usage
from ..schemas.commun import SuppressionOut
from ..schemas.heure import HeureIn, HeureOut

router = APIRouter(prefix="/heures", tags=["heures"])


@router.get("", response_model=list[HeureOut], summary="Lister les créneaux (par heure de début)")
def lister(cas: ListerHeures = cas_usage(ListerHeures)):
    return cas.executer()


@router.get("/{id}", response_model=HeureOut, summary="Voir un créneau")
def voir(id: str, cas: VoirHeure = cas_usage(VoirHeure)):
    return cas.executer(id)


@router.post("", status_code=201, response_model=HeureOut, summary="Créer un créneau")
def creer(payload: HeureIn, cas: CreerHeure = cas_usage(CreerHeure)):
    return cas.executer(payload.model_dump())


@router.put("/{id}", response_model=HeureOut, summary="Modifier un créneau")
def modifier(id: str, payload: HeureIn, cas: ModifierHeure = cas_usage(ModifierHeure)):
    return cas.executer(id, payload.model_dump())


@router.delete("/{id}", response_model=SuppressionOut, summary="Supprimer le créneau et ses séances")
def supprimer(id: str, cas: SupprimerHeure = cas_usage(SupprimerHeure)):
    return cas.executer(id)
