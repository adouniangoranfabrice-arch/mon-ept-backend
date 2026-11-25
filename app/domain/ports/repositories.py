"""Interfaces de stockage : CE DONT le cœur a besoin, sans dire comment c'est fait.

Implémentations : infrastructure/sqlite/repositories/ (application) et tests/unit/fakes.py (tests).
"""
from dataclasses import dataclass
from typing import Protocol, TypeVar

from ..entities import Classe, Eleve, EmploiDuTemps, Evaluation, Heure, Jour, Note, Seance
from .fichiers import LecteurListeEleves
from .identifiants import GenerateurId

T = TypeVar("T")


class Repository(Protocol[T]):
    """Opérations communes à chaque table."""

    def obtenir(self, id: str) -> T | None: ...

    def ajouter(self, entite: T) -> T:
        """Lève Conflit si une contrainte d'unicité est violée."""
        ...

    def modifier(self, entite: T) -> T: ...

    def supprimer(self, id: str) -> None: ...


class JourRepository(Repository[Jour], Protocol): ...


class HeureRepository(Repository[Heure], Protocol): ...


class ClasseRepository(Repository[Classe], Protocol): ...


class EleveRepository(Repository[Eleve], Protocol):
    def ajouter_plusieurs(self, eleves: list[Eleve]) -> list[Eleve]:
        """Ajoute une liste d'élèves en une seule opération (import)."""
        ...

    def supprimer_par_classe(self, classe_id: str) -> int:
        """Supprime les élèves d'une classe ; renvoie leur nombre."""
        ...


class EvaluationRepository(Repository[Evaluation], Protocol):
    def supprimer_par_classe(self, classe_id: str) -> int:
        """Supprime les évaluations d'une classe ; renvoie leur nombre."""
        ...


class NoteRepository(Protocol):
    def lister_par_evaluation(self, evaluation_id: str) -> list[Note]: ...

    def remplacer_pour_evaluation(self, evaluation_id: str, notes: list[Note]) -> None:
        """Remplace toutes les notes d'une évaluation (saisie du tableau de notes)."""
        ...

    def supprimer_par_evaluations(self, evaluation_ids: list[str]) -> int: ...

    def supprimer_par_eleves(self, eleve_ids: list[str]) -> int: ...


class SeanceRepository(Repository[Seance], Protocol):
    def supprimer_liees(self, champ: str, id: str) -> int:
        """Supprime les séances dont `champ` (jour_id, heure_id, classe_id) vaut `id` ; renvoie leur nombre."""
        ...


class EmploiDuTempsRepository(Protocol):
    """Accès à l'ensemble des données (lecture globale, import)."""

    def charger(self, notes: bool = False) -> EmploiDuTemps:
        """Toutes les données. Les notes (nombreuses) ne sont chargées que si `notes` est vrai."""
        ...

    def remplacer_tout(self, edt: EmploiDuTemps) -> None:
        """Remplace toutes les données en une seule opération."""
        ...


@dataclass
class Depots:
    """Toutes les implémentations choisies au démarrage (main.py, scripts/) :
    les repositories, la génération d'identifiants et la lecture des fichiers d'élèves."""

    emploi_du_temps: EmploiDuTempsRepository
    jours: JourRepository
    heures: HeureRepository
    classes: ClasseRepository
    eleves: EleveRepository
    evaluations: EvaluationRepository
    notes: NoteRepository
    seances: SeanceRepository
    generer_id: GenerateurId
    lecteur_eleves: LecteurListeEleves

    def de(self, table: str) -> Repository:
        return getattr(self, table)
