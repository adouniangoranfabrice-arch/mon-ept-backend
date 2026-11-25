from .commun import Entree, Sortie


class HeureIn(Entree):
    code: str = ""
    heure_debut: str = ""
    heure_fin: str = ""


class HeureOut(Sortie):
    id: str
    code: str
    heure_debut: str
    heure_fin: str
