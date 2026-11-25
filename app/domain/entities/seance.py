"""Séance : une classe, un jour, un créneau."""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, ClassVar

from .commun import texte

if TYPE_CHECKING:
    from .emploi_du_temps import EmploiDuTemps


@dataclass
class Seance:
    TABLE: ClassVar[str] = "seances"

    id: str | None
    jour_id: str
    heure_id: str
    classe_id: str
    salle: str = ""
    recurrente: bool = True

    def normalise(self) -> Seance:
        return replace(self, salle=texte(self.salle), recurrente=bool(self.recurrente))

    def meme_creneau(self, autre: Seance) -> bool:
        return self.jour_id == autre.jour_id and self.heure_id == autre.heure_id

    def erreur(self, edt: EmploiDuTemps) -> str | None:
        """Un seul cours par jour et par créneau (un seul enseignant)."""
        if not any(j.id == self.jour_id for j in edt.jours):
            return "Choisissez un jour."
        if not any(h.id == self.heure_id for h in edt.heures):
            return "Choisissez une heure."
        if not any(c.id == self.classe_id for c in edt.classes):
            return "Choisissez une classe."
        conflit = next((x for x in edt.autres(self) if self.meme_creneau(x)), None)
        if conflit:
            c = next((k for k in edt.classes if k.id == conflit.classe_id), None)
            return f"Ce créneau est déjà pris par {c.nom if c else 'une autre classe'}."
        return None
