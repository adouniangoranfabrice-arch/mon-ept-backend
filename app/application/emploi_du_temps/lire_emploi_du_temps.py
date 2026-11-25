"""Lire tout l'emploi du temps, dans l'ordre d'affichage."""
from ...domain.entities import EmploiDuTemps
from ..commun.crud import CasUsage


class LireEmploiDuTemps(CasUsage):
    def executer(self) -> EmploiDuTemps:
        return self.depots.emploi_du_temps.charger(notes=True).trie()
