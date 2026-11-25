"""Assemble les repositories SQLite (utilisé par main.py et scripts/)."""
from pathlib import Path

from sqlalchemy import Engine

from ...domain.ports.repositories import Depots
from ..excel.lecteur_eleves import LecteurExcelEleves
from ..identifiants import generer_uuid
from .client import creer_fabrique_sessions, creer_moteur
from .repositories.classe_repository import SqlClasseRepository
from .repositories.eleve_repository import SqlEleveRepository
from .repositories.emploi_du_temps_repository import SqlEmploiDuTempsRepository
from .repositories.evaluation_repository import SqlEvaluationRepository
from .repositories.heure_repository import SqlHeureRepository
from .repositories.jour_repository import SqlJourRepository
from .repositories.note_repository import SqlNoteRepository
from .repositories.seance_repository import SqlSeanceRepository


def creer_depots_sqlite(chemin: Path) -> tuple[Engine, Depots]:
    moteur = creer_moteur(chemin)
    sessions = creer_fabrique_sessions(moteur)
    return moteur, Depots(
        emploi_du_temps=SqlEmploiDuTempsRepository(sessions),
        jours=SqlJourRepository(sessions),
        heures=SqlHeureRepository(sessions),
        classes=SqlClasseRepository(sessions),
        eleves=SqlEleveRepository(sessions),
        evaluations=SqlEvaluationRepository(sessions),
        notes=SqlNoteRepository(sessions),
        seances=SqlSeanceRepository(sessions),
        generer_id=generer_uuid,
        lecteur_eleves=LecteurExcelEleves(),
    )
