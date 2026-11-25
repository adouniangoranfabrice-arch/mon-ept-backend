"""Assemble les repositories MongoDB."""
from pymongo.database import Database

from ...domain.ports.repositories import Depots
from ..excel.lecteur_eleves import LecteurExcelEleves
from ..identifiants import generer_uuid
from .repositories.classe_repository import MongoClasseRepository
from .repositories.eleve_repository import MongoEleveRepository
from .repositories.emploi_du_temps_repository import MongoEmploiDuTempsRepository
from .repositories.evaluation_repository import MongoEvaluationRepository
from .repositories.heure_repository import MongoHeureRepository
from .repositories.jour_repository import MongoJourRepository
from .repositories.note_repository import MongoNoteRepository
from .repositories.seance_repository import MongoSeanceRepository


def creer_depots_mongo(db: Database) -> Depots:
    return Depots(
        emploi_du_temps=MongoEmploiDuTempsRepository(db),
        jours=MongoJourRepository(db),
        heures=MongoHeureRepository(db),
        classes=MongoClasseRepository(db),
        eleves=MongoEleveRepository(db),
        evaluations=MongoEvaluationRepository(db),
        notes=MongoNoteRepository(db),
        seances=MongoSeanceRepository(db),
        generer_id=generer_uuid,
        lecteur_eleves=LecteurExcelEleves(),
    )
