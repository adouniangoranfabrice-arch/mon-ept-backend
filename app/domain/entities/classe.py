"""Classe d'élèves (6e 1, Tle D…)."""
from __future__ import annotations

import re
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, ClassVar

from .commun import meme, texte

if TYPE_CHECKING:
    from .emploi_du_temps import EmploiDuTemps

COULEUR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
NIVEAUX = ["Sixième", "Cinquième", "Quatrième", "Troisième", "Seconde", "Première", "Terminale"]
# Rang d'après le début du nom : 6e = 0 … Tle = 6
_PREFIXES = [r"^6", r"^5", r"^4", r"^3", r"^(2|sec)", r"^(1|pre|pré)", r"^t"]


@dataclass
class Classe:
    TABLE: ClassVar[str] = "classes"

    id: str | None
    nom: str
    niveau: str = ""
    effectif: int | None = None
    couleur: str = ""

    def normalise(self) -> Classe:
        return replace(self, nom=texte(self.nom), niveau=texte(self.niveau), couleur=texte(self.couleur))

    @property
    def rang(self) -> int:
        """Position de la 6e (0) à la Terminale (6), d'après le nom, sinon le niveau."""
        nom = self.nom.strip().lower()
        for i, p in enumerate(_PREFIXES):
            if re.match(p, nom):
                return i
        return NIVEAUX.index(self.niveau) if self.niveau in NIVEAUX else len(NIVEAUX)

    def cle_tri(self):
        """6e 2 avant 6e 10, puis 5e…, jusqu'à Tle."""
        naturel = [int(x) if x.isdigit() else x.casefold() for x in re.split(r"(\d+)", self.nom)]
        return (self.rang, naturel)

    def erreur(self, edt: EmploiDuTemps) -> str | None:
        autres = edt.autres(self)
        if not self.nom:
            return "Le nom de la classe est obligatoire."
        if any(meme(x.nom, self.nom) for x in autres):
            return f"La classe {self.nom} existe déjà."
        if self.effectif is not None and (not isinstance(self.effectif, int) or self.effectif < 0):
            return "L'effectif doit être un nombre entier positif."
        if not COULEUR_RE.match(self.couleur):
            return "Choisissez une couleur."
        return None
