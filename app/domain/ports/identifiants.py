"""Génération des identifiants (implémentation : infrastructure/identifiants.py)."""
from typing import Callable

GenerateurId = Callable[[], str]
