"""Élève inscrit dans une classe."""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, ClassVar

from .commun import texte

if TYPE_CHECKING:
    from .emploi_du_temps import EmploiDuTemps


def nettoyer_nom(v) -> str:
    """Espaces multiples réduits, bords retirés."""
    return re.sub(r"\s+", " ", texte(v if isinstance(v, str) else ("" if v is None else str(v))))


def cle_nom(nom: str) -> str:
    """Clé de comparaison : sans accents, sans majuscules, espaces normalisés."""
    sans_accents = "".join(c for c in unicodedata.normalize("NFD", nom) if unicodedata.category(c) != "Mn")
    return nettoyer_nom(sans_accents).casefold()


@dataclass
class Eleve:
    TABLE: ClassVar[str] = "eleves"

    id: str | None
    nom_prenoms: str
    classe_id: str

    def normalise(self) -> Eleve:
        return replace(self, nom_prenoms=nettoyer_nom(self.nom_prenoms), classe_id=texte(self.classe_id))

    def meme_eleve(self, autre: Eleve) -> bool:
        """Même nom (sans tenir compte des accents ni des majuscules) dans la même classe."""
        return self.classe_id == autre.classe_id and cle_nom(self.nom_prenoms) == cle_nom(autre.nom_prenoms)

    def erreur(self, edt: EmploiDuTemps) -> str | None:
        if not self.nom_prenoms:
            return "Le nom et les prénoms de l'élève sont obligatoires."
        if len(self.nom_prenoms) > 120:
            return "Le nom et les prénoms ne doivent pas dépasser 120 caractères."
        classe = next((c for c in edt.classes if c.id == self.classe_id), None)
        if classe is None:
            return "Choisissez une classe."
        if any(self.meme_eleve(x) for x in edt.autres(self)):
            return f"« {self.nom_prenoms} » est déjà inscrit(e) en {classe.nom}."
        return None
