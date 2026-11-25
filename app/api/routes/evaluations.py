"""Routes /api/evaluations — évaluations et saisie de leurs notes."""
from fastapi import APIRouter

from ...application.evaluations.creer_evaluation import CreerEvaluation
from ...application.evaluations.lister_evaluations import ListerEvaluations
from ...application.evaluations.modifier_evaluation import ModifierEvaluation
from ...application.evaluations.supprimer_evaluation import SupprimerEvaluation
from ...application.evaluations.voir_evaluation import VoirEvaluation
from ...application.notes.enregistrer_notes import EnregistrerNotes
from ..dependencies import cas_usage
from ..schemas.commun import SuppressionOut
from ..schemas.evaluation import EvaluationIn, EvaluationOut, NoteOut, SaisieNotesIn

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.get("", response_model=list[EvaluationOut], summary="Lister les évaluations")
def lister(cas: ListerEvaluations = cas_usage(ListerEvaluations)):
    return cas.executer()


@router.get("/{id}", response_model=EvaluationOut, summary="Voir une évaluation")
def voir(id: str, cas: VoirEvaluation = cas_usage(VoirEvaluation)):
    return cas.executer(id)


@router.post("", status_code=201, response_model=EvaluationOut, summary="Créer une évaluation")
def creer(payload: EvaluationIn, cas: CreerEvaluation = cas_usage(CreerEvaluation)):
    return cas.executer(payload.model_dump())


@router.put("/{id}", response_model=EvaluationOut, summary="Modifier une évaluation")
def modifier(id: str, payload: EvaluationIn, cas: ModifierEvaluation = cas_usage(ModifierEvaluation)):
    return cas.executer(id, payload.model_dump())


@router.delete("/{id}", response_model=SuppressionOut, summary="Supprimer une évaluation et ses notes")
def supprimer(id: str, cas: SupprimerEvaluation = cas_usage(SupprimerEvaluation)):
    return cas.executer(id)


@router.put("/{id}/notes", response_model=list[NoteOut], summary="Enregistrer les notes d'une évaluation")
def enregistrer_notes(id: str, payload: SaisieNotesIn, cas: EnregistrerNotes = cas_usage(EnregistrerNotes)):
    return cas.executer(id, [n.model_dump() for n in payload.notes])
