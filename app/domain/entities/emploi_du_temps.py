"""EmploiDuTemps : l'ensemble des données d'un enseignant, et les règles qui portent sur cet ensemble."""
from __future__ import annotations

from dataclasses import MISSING, dataclass, field, fields

from ..errors import ErreurValidation
from .classe import Classe
from .eleve import Eleve, cle_nom
from .evaluation import Evaluation
from .heure import Heure
from .jour import Jour
from .note import Note
from .seance import Seance

Entite = Jour | Heure | Classe | Eleve | Evaluation | Note | Seance

# Ordre logique : chaque table ne dépend que des précédentes
TABLES: tuple[str, ...] = ("jours", "heures", "classes", "eleves", "evaluations", "notes", "seances")
ENTITES: dict[str, type] = {
    "jours": Jour, "heures": Heure, "classes": Classe, "eleves": Eleve,
    "evaluations": Evaluation, "notes": Note, "seances": Seance,
}
NOMS: dict[str, str] = {
    "jours": "jour", "heures": "créneau", "classes": "classe", "eleves": "élève",
    "evaluations": "évaluation", "notes": "note", "seances": "séance",
}
# Champ des séances qui pointe vers chaque table de référence
LIEN_SEANCE: dict[str, str] = {"jours": "jour_id", "heures": "heure_id", "classes": "classe_id"}


@dataclass
class EmploiDuTemps:
    jours: list[Jour] = field(default_factory=list)
    heures: list[Heure] = field(default_factory=list)
    classes: list[Classe] = field(default_factory=list)
    eleves: list[Eleve] = field(default_factory=list)
    evaluations: list[Evaluation] = field(default_factory=list)
    notes: list[Note] = field(default_factory=list)
    seances: list[Seance] = field(default_factory=list)

    def liste(self, table: str) -> list:
        return getattr(self, table)

    def par_id(self, table: str) -> dict:
        """Index {id: élément} d'une table (reconstruit si la liste a changé de taille)."""
        cache = self.__dict__.setdefault("_index", {})
        liste = self.liste(table)
        if table not in cache or cache[table][0] != len(liste):
            cache[table] = (len(liste), {x.id: x for x in liste})
        return cache[table][1]

    def autres(self, entite: Entite) -> list:
        """Les éléments de la même table, sauf celui-ci (utile pour les règles d'unicité)."""
        return [x for x in self.liste(entite.TABLE) if x.id != entite.id]

    def verifier(self, entite: Entite) -> None:
        """Lève ErreurValidation si l'entité ne peut pas entrer dans cet emploi du temps."""
        if message := entite.erreur(self):
            raise ErreurValidation(message)

    def trie(self) -> EmploiDuTemps:
        """Ordre d'affichage : lundi → dimanche, H1 → H8, 6e → Tle, élèves par classe puis nom,
        évaluations par classe, trimestre puis date, séances par jour puis heure."""
        jours = sorted(self.jours, key=lambda j: j.ordre)
        heures = sorted(self.heures, key=lambda h: h.heure_debut)
        ordre_j = {j.id: j.ordre for j in jours}
        debut_h = {h.id: h.heure_debut for h in heures}
        classes = sorted(self.classes, key=Classe.cle_tri)
        rang_c = {c.id: i for i, c in enumerate(classes)}
        return EmploiDuTemps(
            jours=jours,
            heures=heures,
            classes=classes,
            eleves=sorted(self.eleves, key=lambda e: (rang_c.get(e.classe_id, 9999), cle_nom(e.nom_prenoms))),
            evaluations=sorted(
                self.evaluations, key=lambda v: (rang_c.get(v.classe_id, 9999), v.trimestre, v.date or "9999", v.libelle)
            ),
            notes=list(self.notes),
            seances=sorted(self.seances, key=lambda s: (ordre_j.get(s.jour_id, 99), debut_h.get(s.heure_id, ""))),
        )

    @classmethod
    def par_defaut(cls) -> EmploiDuTemps:
        """Données de départ : lundi, mardi, jeudi actifs ; 8 créneaux ; une classe."""
        noms = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        actifs = {"Lundi", "Mardi", "Jeudi"}
        creneaux = [
            ("07:30", "08:30"), ("08:30", "09:30"), ("09:30", "10:30"), ("10:45", "11:45"),
            ("11:45", "12:45"), ("15:00", "16:00"), ("16:00", "17:00"), ("17:00", "18:00"),
        ]
        return cls(
            jours=[Jour(id=f"j{i}", libelle=n, ordre=i, actif=n in actifs) for i, n in enumerate(noms, start=1)],
            heures=[Heure(id=f"h{i}", code=f"H{i}", heure_debut=d, heure_fin=f) for i, (d, f) in enumerate(creneaux, 1)],
            classes=[Classe(id="c1", nom="Tle D", niveau="Terminale", effectif=45, couleur="#4C6EF5")],
        )


def depuis_dict(table: str, donnees: dict) -> Entite:
    """Construit l'entité d'une table à partir d'un dictionnaire (clés inconnues ignorées)."""
    cls = ENTITES[table]
    noms = {f.name for f in fields(cls)}
    try:
        return cls(**{"id": None, **{k: v for k, v in donnees.items() if k in noms}})
    except TypeError:
        manquants = [f.name for f in fields(cls) if f.default is MISSING and f.name not in donnees and f.name != "id"]
        raise ErreurValidation(f"Champ(s) manquant(s) pour {NOMS[table]} : {', '.join(manquants)}.") from None
