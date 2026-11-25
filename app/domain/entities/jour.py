"""Jour de la semaine."""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, ClassVar

from .commun import meme, texte

if TYPE_CHECKING:
    from .emploi_du_temps import EmploiDuTemps


@dataclass
class Jour:
    TABLE: ClassVar[str] = "jours"

    id: str | None
    libelle: str
    ordre: int  # 1 = lundi … 7 = dimanche
    actif: bool = True

    def normalise(self) -> Jour:
        return replace(self, libelle=texte(self.libelle), actif=bool(self.actif))

    def erreur(self, edt: EmploiDuTemps) -> str | None:
        """Message d'erreur si ce jour est invalide dans l'emploi du temps, sinon None."""
        autres = edt.autres(self)
        if not self.libelle:
            return "Le libellé est obligatoire."
        if any(meme(x.libelle, self.libelle) for x in autres):
            return f"« {self.libelle} » existe déjà."
        if not isinstance(self.ordre, int) or not 1 <= self.ordre <= 7:
            return "L'ordre doit être un entier entre 1 (lundi) et 7 (dimanche)."
        if any(x.ordre == self.ordre for x in autres):
            return f"L'ordre {self.ordre} est déjà utilisé."
        return None
