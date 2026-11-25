"""Comportement commun des cas d'usage Lister / Voir / Créer / Modifier / Supprimer.

Chaque action concrète (ex. application/classes/creer_classe.py) hérite d'une de ces
classes et précise sa table. Les règles propres à chaque entité sont dans le domaine.
"""
from dataclasses import dataclass, replace
from typing import ClassVar

from ...domain.entities import LIEN_SEANCE, NOMS, Entite, depuis_dict
from ...domain.errors import Introuvable
from ...domain.ports.repositories import Depots


class CasUsage:
    def __init__(self, depots: Depots):
        self.depots = depots


class _ParTable(CasUsage):
    table: ClassVar[str]

    def _exiger(self, id: str) -> Entite:
        entite = self.depots.de(self.table).obtenir(id)
        if entite is None:
            raise Introuvable(f"{NOMS[self.table].capitalize()} introuvable.")
        return entite


class ListerElements(_ParTable):
    def executer(self) -> list[Entite]:
        return self.depots.emploi_du_temps.charger().trie().liste(self.table)


class VoirElement(_ParTable):
    def executer(self, id: str) -> Entite:
        return self._exiger(id)


class CreerElement(_ParTable):
    def executer(self, donnees: dict) -> Entite:
        entite = depuis_dict(self.table, {**donnees, "id": None}).normalise()
        self.depots.emploi_du_temps.charger().verifier(entite)
        return self.depots.de(self.table).ajouter(replace(entite, id=self.depots.generer_id()))


class ModifierElement(_ParTable):
    def executer(self, id: str, donnees: dict) -> Entite:
        self._exiger(id)
        entite = depuis_dict(self.table, {**donnees, "id": id}).normalise()
        self.depots.emploi_du_temps.charger().verifier(entite)
        return self.depots.de(self.table).modifier(entite)


@dataclass
class ResultatSuppression:
    id: str
    seances_supprimees: int
    eleves_supprimes: int = 0
    evaluations_supprimees: int = 0
    notes_supprimees: int = 0


class SupprimerElement(_ParTable):
    """Suppression en cascade :
    - jour, créneau ou classe → ses séances ;
    - classe → ses élèves, ses évaluations et leurs notes ;
    - élève → ses notes ;  évaluation → ses notes."""

    def executer(self, id: str) -> ResultatSuppression:
        self._exiger(id)
        r = ResultatSuppression(id=id, seances_supprimees=0)
        if champ := LIEN_SEANCE.get(self.table):
            r.seances_supprimees = self.depots.seances.supprimer_liees(champ, id)
        if self.table == "classes":
            evaluations = [v.id for v in self.depots.emploi_du_temps.charger().evaluations if v.classe_id == id]
            r.notes_supprimees = self.depots.notes.supprimer_par_evaluations(evaluations)
            r.evaluations_supprimees = self.depots.evaluations.supprimer_par_classe(id)
            r.eleves_supprimes = self.depots.eleves.supprimer_par_classe(id)
        if self.table == "eleves":
            r.notes_supprimees = self.depots.notes.supprimer_par_eleves([id])
        if self.table == "evaluations":
            r.notes_supprimees = self.depots.notes.supprimer_par_evaluations([id])
        self.depots.de(self.table).supprimer(id)
        return r
