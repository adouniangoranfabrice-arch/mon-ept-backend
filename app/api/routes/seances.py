"""Routes /api/seances — chaque route appelle un seul cas d'usage."""
from fastapi import APIRouter

from ...application.seances.creer_seance import CreerSeance
from ...application.seances.lister_seances import ListerSeances
from ...application.seances.modifier_seance import ModifierSeance
from ...application.seances.supprimer_seance import SupprimerSeance
from ...application.seances.voir_seance import VoirSeance
from ..dependencies import cas_usage
from ..schemas.commun import SuppressionOut
from ..schemas.seance import SeanceIn, SeanceOut

router = APIRouter(prefix="/seances", tags=["seances"])


@router.get("", response_model=list[SeanceOut], summary="Lister les séances (par jour puis heure)")
def lister(cas: ListerSeances = cas_usage(ListerSeances)):
    return cas.executer()


@router.get("/{id}", response_model=SeanceOut, summary="Voir une séance")
def voir(id: str, cas: VoirSeance = cas_usage(VoirSeance)):
    return cas.executer(id)


@router.post("", status_code=201, response_model=SeanceOut, summary="Créer une séance")
def creer(payload: SeanceIn, cas: CreerSeance = cas_usage(CreerSeance)):
    return cas.executer(payload.model_dump())


@router.put("/{id}", response_model=SeanceOut, summary="Modifier une séance")
def modifier(id: str, payload: SeanceIn, cas: ModifierSeance = cas_usage(ModifierSeance)):
    return cas.executer(id, payload.model_dump())


@router.delete("/{id}", response_model=SuppressionOut, summary="Supprimer la séance")
def supprimer(id: str, cas: SupprimerSeance = cas_usage(SupprimerSeance)):
    return cas.executer(id)
