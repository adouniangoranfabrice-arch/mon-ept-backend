"""Note d'un élève à une évaluation, et calcul des moyennes."""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, ClassVar, Iterable

if TYPE_CHECKING:
    from .emploi_du_temps import EmploiDuTemps
    from .evaluation import Evaluation


@dataclass
class Note:
    TABLE: ClassVar[str] = "notes"

    id: str | None
    evaluation_id: str
    eleve_id: str
    valeur: float

    def normalise(self) -> Note:
        valeur = round(float(self.valeur), 2) if isinstance(self.valeur, (int, float)) else self.valeur
        return replace(self, valeur=valeur)

    def erreur(self, edt: EmploiDuTemps) -> str | None:
        """Unicité (une note par élève et par évaluation) : vérifiée par l'import et la saisie."""
        evaluation = edt.par_id("evaluations").get(self.evaluation_id)
        if evaluation is None:
            return "Évaluation introuvable."
        eleve = edt.par_id("eleves").get(self.eleve_id)
        if eleve is None:
            return "Élève introuvable."
        if eleve.classe_id != evaluation.classe_id:
            classe = edt.par_id("classes").get(evaluation.classe_id)
            return f"{eleve.nom_prenoms} n'est pas inscrit(e) en {classe.nom if classe else 'cette classe'}."
        if not isinstance(self.valeur, (int, float)) or not 0 <= self.valeur <= evaluation.bareme:
            return f"Note de {eleve.nom_prenoms} : elle doit être comprise entre 0 et {evaluation.bareme:g}."
        return None


def moyenne(notes: Iterable[tuple[Note, Evaluation]]) -> float | None:
    """Moyenne sur 20, pondérée par les coefficients. None s'il n'y a aucune note."""
    total = poids = 0.0
    for note, evaluation in notes:
        total += evaluation.sur_20(note.valeur) * evaluation.coefficient
        poids += evaluation.coefficient
    return round(total / poids, 2) if poids else None


def moyenne_annuelle(moyennes_trimestres: Iterable[float | None]) -> float | None:
    """Moyenne des trimestres qui ont une moyenne."""
    valeurs = [m for m in moyennes_trimestres if m is not None]
    return round(sum(valeurs) / len(valeurs), 2) if valeurs else None
