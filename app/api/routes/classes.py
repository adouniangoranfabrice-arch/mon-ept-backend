"""Routes /api/classes — chaque route appelle un seul cas d'usage."""
from fastapi import APIRouter

from ...application.classes.creer_classe import CreerClasse
from ...application.classes.lister_classes import ListerClasses
from ...application.classes.modifier_classe import ModifierClasse
from ...application.classes.supprimer_classe import SupprimerClasse
from ...application.classes.voir_classe import VoirClasse
from ..dependencies import cas_usage
from ..schemas.commun import SuppressionOut
from ..schemas.classe import ClasseIn, ClasseOut

router = APIRouter(prefix="/classes", tags=["classes"])


@router.get("", response_model=list[ClasseOut], summary="Lister les classes (6e → Tle)")
def lister(cas: ListerClasses = cas_usage(ListerClasses)):
    return cas.executer()


@router.get("/{id}", response_model=ClasseOut, summary="Voir une classe")
def voir(id: str, cas: VoirClasse = cas_usage(VoirClasse)):
    return cas.executer(id)


@router.post("", status_code=201, response_model=ClasseOut, summary="Créer une classe")
def creer(payload: ClasseIn, cas: CreerClasse = cas_usage(CreerClasse)):
    return cas.executer(payload.model_dump())


@router.put("/{id}", response_model=ClasseOut, summary="Modifier une classe")
def modifier(id: str, payload: ClasseIn, cas: ModifierClasse = cas_usage(ModifierClasse)):
    return cas.executer(id, payload.model_dump())


@router.delete("/{id}", response_model=SuppressionOut, summary="Supprimer la classe et ses séances")
def supprimer(id: str, cas: SupprimerClasse = cas_usage(SupprimerClasse)):
    return cas.executer(id)
