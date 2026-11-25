"""Petits outils partagés par les entités."""


def texte(v) -> str:
    """Chaîne nettoyée (None → "")."""
    return v.strip() if isinstance(v, str) else ""


def meme(a: str, b: str) -> bool:
    """Comparaison sans tenir compte des majuscules."""
    return a.casefold() == b.casefold()
