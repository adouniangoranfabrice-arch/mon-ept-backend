"""Vider l'emploi du temps : supprime tous les jours, heures, classes et séances (pour tout ressaisir)."""
from ...domain.entities import EmploiDuTemps
from ..commun.crud import CasUsage


class ViderEmploiDuTemps(CasUsage):
    def executer(self) -> EmploiDuTemps:
        self.depots.emploi_du_temps.remplacer_tout(EmploiDuTemps())
        return self.depots.emploi_du_temps.charger(notes=True)
