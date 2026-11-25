"""Lecture de fichiers fournis par l'utilisateur (implémentation : infrastructure/excel/)."""
from typing import Protocol


class LecteurListeEleves(Protocol):
    def lire_noms(self, contenu: bytes, nom_fichier: str) -> list[str]:
        """Noms et prénoms trouvés dans le fichier (colonne « Nom_prenoms »), dans l'ordre.

        Lève ErreurValidation si le fichier est illisible ou si la colonne est introuvable.
        """
        ...
