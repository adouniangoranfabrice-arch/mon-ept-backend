"""Faux repositories en mémoire : implémentent les ports sans base de données."""
from copy import deepcopy
from itertools import count

from app.domain.entities import EmploiDuTemps
from app.domain.errors import Conflit
from app.domain.ports.repositories import Depots


class _Stockage:
    def __init__(self, edt: EmploiDuTemps):
        self.edt = deepcopy(edt)


class FauxRepository:
    def __init__(self, stockage: _Stockage, table: str):
        self._st, self._table = stockage, table

    @property
    def _liste(self) -> list:
        return self._st.edt.liste(self._table)

    def obtenir(self, id):
        return deepcopy(next((e for e in self._liste if e.id == id), None))

    def ajouter(self, entite):
        if self._table == "seances" and any(s.meme_creneau(entite) for s in self._liste):
            raise Conflit("Conflit avec des données existantes (créneau déjà pris ?).")
        self._liste.append(deepcopy(entite))
        return entite

    def modifier(self, entite):
        self._liste[:] = [deepcopy(entite) if e.id == entite.id else e for e in self._liste]
        return entite

    def supprimer(self, id):
        self._liste[:] = [e for e in self._liste if e.id != id]


class FauxSeanceRepository(FauxRepository):
    def supprimer_liees(self, champ, id):
        avant = len(self._liste)
        self._liste[:] = [s for s in self._liste if getattr(s, champ) != id]
        return avant - len(self._liste)


class FauxEleveRepository(FauxRepository):
    def ajouter_plusieurs(self, eleves):
        self._liste.extend(deepcopy(eleves))
        return eleves

    def supprimer_par_classe(self, classe_id):
        avant = len(self._liste)
        self._liste[:] = [e for e in self._liste if e.classe_id != classe_id]
        return avant - len(self._liste)


class FauxEvaluationRepository(FauxRepository):
    def supprimer_par_classe(self, classe_id):
        avant = len(self._liste)
        self._liste[:] = [v for v in self._liste if v.classe_id != classe_id]
        return avant - len(self._liste)


class FauxNoteRepository:
    def __init__(self, stockage: _Stockage):
        self._st = stockage

    def _garder(self, condition):
        avant = len(self._st.edt.notes)
        self._st.edt.notes = [n for n in self._st.edt.notes if condition(n)]
        return avant - len(self._st.edt.notes)

    def lister_par_evaluation(self, evaluation_id):
        return [deepcopy(n) for n in self._st.edt.notes if n.evaluation_id == evaluation_id]

    def remplacer_pour_evaluation(self, evaluation_id, notes):
        self._garder(lambda n: n.evaluation_id != evaluation_id)
        self._st.edt.notes.extend(deepcopy(notes))

    def supprimer_par_evaluations(self, evaluation_ids):
        return self._garder(lambda n: n.evaluation_id not in evaluation_ids)

    def supprimer_par_eleves(self, eleve_ids):
        return self._garder(lambda n: n.eleve_id not in eleve_ids)


class FauxLecteurEleves:
    """Une ligne de texte = un nom (pas besoin d'un vrai fichier Excel dans les tests unitaires)."""

    def lire_noms(self, contenu, nom_fichier):
        return contenu.decode("utf-8").splitlines()


class FauxEmploiDuTempsRepository:
    def __init__(self, stockage: _Stockage):
        self._st = stockage

    def charger(self, notes=False):
        edt = deepcopy(self._st.edt)
        if not notes:
            edt.notes = []
        return edt

    def remplacer_tout(self, edt):
        self._st.edt = deepcopy(edt)


def faux_depots(edt: EmploiDuTemps | None = None) -> Depots:
    st = _Stockage(edt if edt is not None else EmploiDuTemps.par_defaut())
    numeros = count(1)
    return Depots(
        emploi_du_temps=FauxEmploiDuTempsRepository(st),
        jours=FauxRepository(st, "jours"),
        heures=FauxRepository(st, "heures"),
        classes=FauxRepository(st, "classes"),
        eleves=FauxEleveRepository(st, "eleves"),
        evaluations=FauxEvaluationRepository(st, "evaluations"),
        notes=FauxNoteRepository(st),
        seances=FauxSeanceRepository(st, "seances"),
        generer_id=lambda: f"id{next(numeros)}",
        lecteur_eleves=FauxLecteurEleves(),
    )
