"""Évaluation (interrogation, devoir…) d'une classe pendant un trimestre."""
from __future__ import annotations

import re
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, ClassVar

from .commun import meme, texte

if TYPE_CHECKING:
    from .emploi_du_temps import EmploiDuTemps

TRIMESTRES = {1: "1er trimestre", 2: "2e trimestre", 3: "3e trimestre"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass
class Evaluation:
    TABLE: ClassVar[str] = "evaluations"

    id: str | None
    classe_id: str
    trimestre: int  # 1, 2 ou 3
    libelle: str  # ex. « Interrogation 1 »
    date: str = ""  # "AAAA-MM-JJ", facultative
    bareme: float = 20  # note maximale
    coefficient: float = 1

    def normalise(self) -> Evaluation:
        return replace(self, classe_id=texte(self.classe_id), libelle=texte(self.libelle), date=texte(self.date))

    def sur_20(self, valeur: float) -> float:
        return valeur / self.bareme * 20

    def erreur(self, edt: EmploiDuTemps) -> str | None:
        classe = edt.par_id("classes").get(self.classe_id)
        if classe is None:
            return "Choisissez une classe."
        if self.trimestre not in TRIMESTRES:
            return "Le trimestre doit être 1, 2 ou 3."
        if not self.libelle:
            return "Le libellé de l'évaluation est obligatoire (ex. Interrogation 1)."
        if len(self.libelle) > 60:
            return "Le libellé ne doit pas dépasser 60 caractères."
        if self.date and not DATE_RE.match(self.date):
            return "La date doit être au format AAAA-MM-JJ."
        if not isinstance(self.bareme, (int, float)) or not 1 <= self.bareme <= 100:
            return "Le barème doit être compris entre 1 et 100."
        if not isinstance(self.coefficient, (int, float)) or not 0 < self.coefficient <= 10:
            return "Le coefficient doit être compris entre 0 (exclu) et 10."
        if any(
            x.classe_id == self.classe_id and x.trimestre == self.trimestre and meme(x.libelle, self.libelle)
            for x in edt.autres(self)
        ):
            return f"« {self.libelle} » existe déjà en {classe.nom} au {TRIMESTRES[self.trimestre]}."
        return None
