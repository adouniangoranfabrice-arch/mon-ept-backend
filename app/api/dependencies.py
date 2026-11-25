"""Injection de dépendances : fournit aux routes les cas d'usage, branchés sur les dépôts choisis dans main.py."""
from typing import Any, TypeVar

from fastapi import Depends, Request

from ..application.commun.crud import CasUsage
from ..domain.ports.repositories import Depots

C = TypeVar("C", bound=CasUsage)


def get_depots(request: Request) -> Depots:
    return request.app.state.depots


def cas_usage(cls: type[C]) -> Any:
    """Dans une route : `cas: CreerClasse = cas_usage(CreerClasse)`."""

    def fournir(depots: Depots = Depends(get_depots)) -> C:
        return cls(depots)

    return Depends(fournir)
