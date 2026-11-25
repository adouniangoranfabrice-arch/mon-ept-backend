"""Inscrire une liste d'élèves dans une classe (après l'aperçu du fichier Excel).

Les élèves déjà inscrits dans la classe (même nom, sans tenir compte des accents ni
des majuscules) sont ignorés ; les autres sont ajoutés en une seule opération.
"""
from dataclasses import dataclass

from ...domain.entities import Eleve
from ...domain.errors import ErreurValidation, Introuvable
from ..commun.crud import CasUsage


@dataclass
class ResultatImportEleves:
    ajoutes: list[Eleve]
    ignores: list[str]  # déjà inscrits dans la classe (ou en double dans la liste)


class ImporterEleves(CasUsage):
    def executer(self, classe_id: str, noms: list[str]) -> ResultatImportEleves:
        edt = self.depots.emploi_du_temps.charger()
        if not any(c.id == classe_id for c in edt.classes):
            raise Introuvable("Classe introuvable.")

        ajoutes, ignores = [], []
        for nom in noms:
            eleve = Eleve(id=None, nom_prenoms=nom, classe_id=classe_id).normalise()
            if not eleve.nom_prenoms:
                continue
            if any(eleve.meme_eleve(x) for x in edt.eleves):
                ignores.append(eleve.nom_prenoms)
                continue
            if message := eleve.erreur(edt):
                raise ErreurValidation(f"« {eleve.nom_prenoms} » : {message}")
            eleve = Eleve(id=self.depots.generer_id(), nom_prenoms=eleve.nom_prenoms, classe_id=classe_id)
            edt.eleves.append(eleve)  # pour repérer les doublons dans la liste elle-même
            ajoutes.append(eleve)

        if ajoutes:
            self.depots.eleves.ajouter_plusieurs(ajoutes)
        return ResultatImportEleves(ajoutes=ajoutes, ignores=ignores)
