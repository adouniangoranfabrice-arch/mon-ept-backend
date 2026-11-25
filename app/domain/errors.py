"""Erreurs métier. La couche API les traduit en codes HTTP (api/errors.py)."""


class ErreurDomaine(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ErreurValidation(ErreurDomaine):
    """Donnée refusée par une règle métier (→ 400)."""


class Introuvable(ErreurDomaine):
    """L'élément demandé n'existe pas (→ 404)."""


class Conflit(ErreurDomaine):
    """Conflit avec les données existantes (→ 409)."""
