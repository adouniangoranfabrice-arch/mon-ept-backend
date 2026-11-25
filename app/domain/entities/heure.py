"""Créneau horaire (H1, H2…)."""
from __future__ import annotations

import re
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, ClassVar

from .commun import meme, texte

if TYPE_CHECKING:
    from .emploi_du_temps import EmploiDuTemps

HEURE_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


def en_minutes(t: str) -> int:
    """« 07:30 » → 450"""
    h, m = t.split(":")
    return int(h) * 60 + int(m)


@dataclass
class Heure:
    TABLE: ClassVar[str] = "heures"

    id: str | None
    code: str
    heure_debut: str  # "HH:MM"
    heure_fin: str

    def normalise(self) -> Heure:
        return replace(
            self, code=texte(self.code).upper(), heure_debut=texte(self.heure_debut), heure_fin=texte(self.heure_fin)
        )

    def chevauche(self, autre: Heure) -> bool:
        return en_minutes(self.heure_debut) < en_minutes(autre.heure_fin) and en_minutes(autre.heure_debut) < en_minutes(
            self.heure_fin
        )

    def erreur(self, edt: EmploiDuTemps) -> str | None:
        autres = edt.autres(self)
        if not self.code:
            return "Le code est obligatoire (ex. H1)."
        if any(meme(x.code, self.code) for x in autres):
            return f"Le code {self.code} existe déjà."
        if not self.heure_debut or not self.heure_fin:
            return "Indiquez l'heure de début et l'heure de fin."
        if not HEURE_RE.match(self.heure_debut) or not HEURE_RE.match(self.heure_fin):
            return "Les heures doivent être au format HH:MM (ex. 07:30)."
        if en_minutes(self.heure_fin) <= en_minutes(self.heure_debut):
            return "L'heure de fin doit être après l'heure de début."
        for x in autres:
            if self.chevauche(x):
                return f"Ce créneau chevauche {x.code} ({x.heure_debut} – {x.heure_fin})."
        return None
