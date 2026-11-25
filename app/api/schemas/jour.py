from .commun import Entree, Sortie


class JourIn(Entree):
    libelle: str = ""
    ordre: int
    actif: bool = True


class JourOut(Sortie):
    id: str
    libelle: str
    ordre: int
    actif: bool
