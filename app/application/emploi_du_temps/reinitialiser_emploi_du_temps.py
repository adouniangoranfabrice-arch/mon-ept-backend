"""Revenir aux données de départ (aussi utilisé pour remplir une base neuve)."""
from ...domain.entities import EmploiDuTemps
from ..commun.crud import CasUsage


class ReinitialiserEmploiDuTemps(CasUsage):
    def executer(self) -> EmploiDuTemps:
        self.depots.emploi_du_temps.remplacer_tout(EmploiDuTemps.par_defaut())
        return self.depots.emploi_du_temps.charger(notes=True).trie()
