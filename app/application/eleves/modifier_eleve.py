"""Modifier un élève (nom, ou changer de classe) — mêmes règles qu'à la création.

Un élève qui change de classe perd ses notes : elles appartiennent aux évaluations
de son ancienne classe.
"""
from ...domain.entities import Eleve
from ..commun.crud import ModifierElement


class ModifierEleve(ModifierElement):
    table = "eleves"

    def executer(self, id: str, donnees: dict) -> Eleve:
        avant = self._exiger(id)
        eleve = super().executer(id, donnees)
        if eleve.classe_id != avant.classe_id:
            self.depots.notes.supprimer_par_eleves([id])
        return eleve
