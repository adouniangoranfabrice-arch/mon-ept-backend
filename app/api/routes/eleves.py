"""Routes /api/eleves — chaque route appelle un seul cas d'usage."""
from fastapi import APIRouter, File, UploadFile

from ...application.eleves.creer_eleve import CreerEleve
from ...application.eleves.importer_eleves import ImporterEleves
from ...application.eleves.lire_fichier_eleves import TAILLE_MAX, LireFichierEleves
from ...application.eleves.lister_eleves import ListerEleves
from ...application.eleves.modifier_eleve import ModifierEleve
from ...application.eleves.supprimer_eleve import SupprimerEleve
from ...application.eleves.voir_eleve import VoirEleve
from ..dependencies import cas_usage
from ..schemas.commun import SuppressionOut
from ..schemas.eleve import ApercuFichierOut, EleveIn, EleveOut, ImportElevesIn, ImportElevesOut

router = APIRouter(prefix="/eleves", tags=["eleves"])


@router.get("", response_model=list[EleveOut], summary="Lister les élèves (par classe puis par nom)")
def lister(cas: ListerEleves = cas_usage(ListerEleves)):
    return cas.executer()


@router.post("/lecture", response_model=ApercuFichierOut, summary="Lire un fichier Excel d'élèves (aperçu, rien n'est enregistré)")
async def lire_fichier(fichier: UploadFile = File(...), cas: LireFichierEleves = cas_usage(LireFichierEleves)):
    contenu = await fichier.read(TAILLE_MAX + 1)
    return cas.executer(contenu, fichier.filename or "")


@router.post("/import", response_model=ImportElevesOut, summary="Inscrire une liste d'élèves dans une classe")
def importer(payload: ImportElevesIn, cas: ImporterEleves = cas_usage(ImporterEleves)):
    return cas.executer(payload.classe_id, payload.noms)


@router.get("/{id}", response_model=EleveOut, summary="Voir un élève")
def voir(id: str, cas: VoirEleve = cas_usage(VoirEleve)):
    return cas.executer(id)


@router.post("", status_code=201, response_model=EleveOut, summary="Ajouter un élève")
def creer(payload: EleveIn, cas: CreerEleve = cas_usage(CreerEleve)):
    return cas.executer(payload.model_dump())


@router.put("/{id}", response_model=EleveOut, summary="Modifier un élève (nom ou classe)")
def modifier(id: str, payload: EleveIn, cas: ModifierEleve = cas_usage(ModifierEleve)):
    return cas.executer(id, payload.model_dump())


@router.delete("/{id}", response_model=SuppressionOut, summary="Supprimer un élève")
def supprimer(id: str, cas: SupprimerEleve = cas_usage(SupprimerEleve)):
    return cas.executer(id)
