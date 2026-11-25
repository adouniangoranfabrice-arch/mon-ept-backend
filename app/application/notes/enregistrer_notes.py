"""Enregistrer les notes d'une évaluation (tableau de saisie).

Remplace toutes les notes de l'évaluation : un élève sans valeur n'a pas de note
(absent, non noté). Tout est validé avant d'enregistrer (tout ou rien).
"""
from ...domain.entities import Note
from ...domain.errors import ErreurValidation, Introuvable
from ..commun.crud import CasUsage


class EnregistrerNotes(CasUsage):
    def executer(self, evaluation_id: str, saisies: list[dict]) -> list[Note]:
        edt = self.depots.emploi_du_temps.charger()
        if evaluation_id not in edt.par_id("evaluations"):
            raise Introuvable("Évaluation introuvable.")

        notes, vus = [], set()
        for saisie in saisies:
            eleve_id, valeur = saisie.get("eleve_id", ""), saisie.get("valeur")
            if eleve_id in vus:
                raise ErreurValidation("Un élève apparaît deux fois dans la saisie.")
            vus.add(eleve_id)
            if valeur is None:
                continue  # pas de note pour cet élève
            note = Note(id=None, evaluation_id=evaluation_id, eleve_id=eleve_id, valeur=valeur).normalise()
            edt.verifier(note)
            notes.append(note)

        notes = [Note(id=self.depots.generer_id(), evaluation_id=n.evaluation_id, eleve_id=n.eleve_id, valeur=n.valeur) for n in notes]
        self.depots.notes.remplacer_pour_evaluation(evaluation_id, notes)
        return notes
