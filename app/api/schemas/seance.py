from .commun import Entree, Sortie


class SeanceIn(Entree):
    jour_id: str = ""
    heure_id: str = ""
    classe_id: str = ""
    salle: str | None = ""
    recurrente: bool = True


class SeanceOut(Sortie):
    id: str
    jour_id: str
    heure_id: str
    classe_id: str
    salle: str
    recurrente: bool
