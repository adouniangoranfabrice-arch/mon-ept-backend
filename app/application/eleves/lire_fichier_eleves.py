"""Lire un fichier Excel d'élèves (colonne « Nom_prenoms ») et préparer l'aperçu avant import."""
from dataclasses import dataclass

from ...domain.entities.eleve import cle_nom, nettoyer_nom
from ...domain.errors import ErreurValidation
from ..commun.crud import CasUsage

TAILLE_MAX = 5 * 1024 * 1024  # 5 Mo
NOMBRE_MAX = 2000


@dataclass
class Apercu:
    noms: list[str]  # noms uniques, nettoyés, dans l'ordre du fichier
    doublons_fichier: int  # lignes ignorées car déjà présentes plus haut dans le fichier


class LireFichierEleves(CasUsage):
    def executer(self, contenu: bytes, nom_fichier: str) -> Apercu:
        if not contenu:
            raise ErreurValidation("Le fichier est vide.")
        if len(contenu) > TAILLE_MAX:
            raise ErreurValidation("Le fichier dépasse 5 Mo.")

        noms, vus, doublons = [], set(), 0
        for brut in self.depots.lecteur_eleves.lire_noms(contenu, nom_fichier):
            nom = nettoyer_nom(brut)
            if not nom:
                continue
            if cle_nom(nom) in vus:
                doublons += 1
                continue
            vus.add(cle_nom(nom))
            noms.append(nom)

        if not noms:
            raise ErreurValidation("Aucun élève trouvé sous la colonne « Nom_prenoms ».")
        if len(noms) > NOMBRE_MAX:
            raise ErreurValidation(f"Trop d'élèves dans le fichier ({len(noms)}, maximum {NOMBRE_MAX}).")
        return Apercu(noms=noms, doublons_fichier=doublons)
