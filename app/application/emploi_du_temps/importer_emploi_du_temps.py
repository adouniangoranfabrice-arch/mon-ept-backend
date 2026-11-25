"""Importer une sauvegarde : remplace toutes les données, après validation complète (tout ou rien)."""
from dataclasses import replace

from ...domain.entities import NOMS, TABLES, EmploiDuTemps, depuis_dict
from ...domain.errors import ErreurValidation
from ..commun.crud import CasUsage


class ImporterEmploiDuTemps(CasUsage):
    def executer(self, donnees: dict[str, list[dict]]) -> EmploiDuTemps:
        accepte = EmploiDuTemps()
        notes_vues: set[tuple[str, str]] = set()
        for table in TABLES:
            ids: set[str] = set()
            for i, brut in enumerate(donnees.get(table, []), start=1):
                entite = depuis_dict(table, brut).normalise()
                entite = replace(entite, id=entite.id or self.depots.generer_id())
                if entite.id in ids:
                    raise ErreurValidation(f"Import refusé : identifiant en double ({NOMS[table]} n°{i}).")
                if table == "notes":
                    cle = (entite.evaluation_id, entite.eleve_id)
                    if cle in notes_vues:
                        raise ErreurValidation(f"Import refusé (note n°{i}) : deux notes pour le même élève et la même évaluation.")
                    notes_vues.add(cle)
                if message := entite.erreur(accepte):
                    raise ErreurValidation(f"Import refusé ({NOMS[table]} n°{i}) : {message}")
                ids.add(entite.id)
                accepte.liste(table).append(entite)
        self.depots.emploi_du_temps.remplacer_tout(accepte)
        return self.depots.emploi_du_temps.charger(notes=True).trie()
