"""create_indexes(), appelé au démarrage."""
from pymongo import ASCENDING
from pymongo.database import Database

COLLECTIONS = ("jours", "heures", "classes", "eleves", "evaluations", "notes", "seances")


MARQUEUR = {"_id": "initialisation"}


def create_indexes(db: Database) -> bool:
    """Crée les index. Renvoie True seulement au tout premier démarrage sur une base neuve
    (à remplir avec les données de départ). Une base vidée volontairement reste vide."""
    db.seances.create_index([("jour_id", ASCENDING), ("heure_id", ASCENDING)], unique=True, name="uq_seance_creneau")
    db.seances.create_index("classe_id", name="seance_classe")
    db.jours.create_index("ordre", unique=True, name="uq_jour_ordre")
    db.heures.create_index("heure_debut", name="heure_debut")
    db.eleves.create_index("classe_id", name="eleve_classe")
    db.evaluations.create_index([("classe_id", ASCENDING), ("trimestre", ASCENDING)], name="evaluation_classe_trimestre")
    db.notes.create_index([("evaluation_id", ASCENDING), ("eleve_id", ASCENDING)], unique=True, name="uq_note_eleve")
    db.notes.create_index("eleve_id", name="note_eleve")

    deja_initialisee = db.meta.find_one(MARQUEUR) is not None
    vide = all(db[c].estimated_document_count() == 0 for c in COLLECTIONS)
    db.meta.update_one(MARQUEUR, {"$setOnInsert": MARQUEUR}, upsert=True)
    return vide and not deja_initialisee
