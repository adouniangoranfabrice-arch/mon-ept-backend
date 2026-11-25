"""Modifier une évaluation (libellé, date, barème, coefficient, trimestre).

Une évaluation déjà notée ne peut pas changer de classe, et son barème ne peut pas
descendre sous une note déjà saisie.
"""
from ...domain.entities import Evaluation
from ...domain.errors import ErreurValidation
from ..commun.crud import ModifierElement


class ModifierEvaluation(ModifierElement):
    table = "evaluations"

    def executer(self, id: str, donnees: dict) -> Evaluation:
        avant = self._exiger(id)
        notes = self.depots.notes.lister_par_evaluation(id)
        if notes:
            if donnees.get("classe_id", avant.classe_id) != avant.classe_id:
                raise ErreurValidation("Cette évaluation a déjà des notes : elle ne peut pas changer de classe.")
            bareme = donnees.get("bareme", avant.bareme)
            plus_haute = max(n.valeur for n in notes)
            if isinstance(bareme, (int, float)) and bareme < plus_haute:
                raise ErreurValidation(f"Le barème ne peut pas être inférieur à la meilleure note saisie ({plus_haute:g}).")
        return super().executer(id, donnees)
