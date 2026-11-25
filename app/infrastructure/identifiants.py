"""Implémentation du port GenerateurId."""
import uuid


def generer_uuid() -> str:
    return str(uuid.uuid4())
