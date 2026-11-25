"""Évaluations et notes : règles, moyennes, saisie et suppressions en cascade (faux dépôts)."""
import pytest

from app.application.classes.supprimer_classe import SupprimerClasse
from app.application.eleves.importer_eleves import ImporterEleves
from app.application.eleves.modifier_eleve import ModifierEleve
from app.application.eleves.supprimer_eleve import SupprimerEleve
from app.application.emploi_du_temps.importer_emploi_du_temps import ImporterEmploiDuTemps
from app.application.emploi_du_temps.lire_emploi_du_temps import LireEmploiDuTemps
from app.application.evaluations.creer_evaluation import CreerEvaluation
from app.application.evaluations.modifier_evaluation import ModifierEvaluation
from app.application.evaluations.supprimer_evaluation import SupprimerEvaluation
from app.application.notes.enregistrer_notes import EnregistrerNotes
from app.domain.entities import Classe, EmploiDuTemps, Evaluation, Note, moyenne, moyenne_annuelle
from app.domain.errors import ErreurValidation

from .fakes import faux_depots


@pytest.fixture()
def depots():
    edt = EmploiDuTemps.par_defaut()
    edt.classes.append(Classe(id="c6", nom="6e 1", couleur="#12B886"))
    d = faux_depots(edt)
    ImporterEleves(d).executer("c1", ["Koné Awa", "Yao Koffi"])  # id1, id2
    ImporterEleves(d).executer("c6", ["Traoré Ali"])  # id3
    return d


def evaluation(depots, **kw):
    return CreerEvaluation(depots).executer({"classe_id": "c1", "trimestre": 1, "libelle": "Interro 1", **kw})


# ---------- Moyennes ----------
def test_moyenne_ponderee_sur_20():
    i1 = Evaluation(id="a", classe_id="c", trimestre=1, libelle="I1", bareme=10, coefficient=1)
    d1 = Evaluation(id="b", classe_id="c", trimestre=1, libelle="D1", bareme=20, coefficient=2)
    notes = [(Note(None, "a", "e", 5), i1), (Note(None, "b", "e", 14), d1)]  # 10/20 (x1) et 14/20 (x2)
    assert moyenne(notes) == round((10 + 28) / 3, 2) == 12.67
    assert moyenne([]) is None
    assert moyenne_annuelle([12, None, 14]) == 13


# ---------- Évaluations ----------
def test_regles_evaluation(depots):
    evaluation(depots)
    with pytest.raises(ErreurValidation, match="existe déjà en Tle D au 1er trimestre"):
        evaluation(depots, libelle="interro 1")
    evaluation(depots, libelle="Interro 1", trimestre=2)  # autre trimestre : permis
    with pytest.raises(ErreurValidation, match="trimestre doit être 1, 2 ou 3"):
        evaluation(depots, trimestre=4)
    with pytest.raises(ErreurValidation, match="barème"):
        evaluation(depots, libelle="X", bareme=0)


# ---------- Saisie des notes ----------
def test_saisie_remplace_les_notes(depots):
    ev = evaluation(depots, bareme=10)
    notes = EnregistrerNotes(depots).executer(ev.id, [{"eleve_id": "id1", "valeur": 7.256}, {"eleve_id": "id2", "valeur": None}])
    assert [(n.eleve_id, n.valeur) for n in notes] == [("id1", 7.26)]

    EnregistrerNotes(depots).executer(ev.id, [{"eleve_id": "id1", "valeur": 8}, {"eleve_id": "id2", "valeur": 9.5}])
    assert sorted((n.eleve_id, n.valeur) for n in LireEmploiDuTemps(depots).executer().notes) == [("id1", 8), ("id2", 9.5)]


def test_saisie_refusee(depots):
    ev = evaluation(depots, bareme=10)
    with pytest.raises(ErreurValidation, match="entre 0 et 10"):
        EnregistrerNotes(depots).executer(ev.id, [{"eleve_id": "id1", "valeur": 12}])
    with pytest.raises(ErreurValidation, match="Traoré Ali n'est pas inscrit\\(e\\) en Tle D"):
        EnregistrerNotes(depots).executer(ev.id, [{"eleve_id": "id3", "valeur": 5}])
    with pytest.raises(ErreurValidation, match="deux fois"):
        EnregistrerNotes(depots).executer(ev.id, [{"eleve_id": "id1", "valeur": 5}, {"eleve_id": "id1", "valeur": 6}])
    assert LireEmploiDuTemps(depots).executer().notes == []  # tout ou rien


def test_modifier_evaluation_deja_notee(depots):
    ev = evaluation(depots)
    EnregistrerNotes(depots).executer(ev.id, [{"eleve_id": "id1", "valeur": 16}])
    base = {"classe_id": "c1", "trimestre": 1, "libelle": "Interro 1"}
    with pytest.raises(ErreurValidation, match="meilleure note saisie \\(16\\)"):
        ModifierEvaluation(depots).executer(ev.id, {**base, "bareme": 10})
    with pytest.raises(ErreurValidation, match="changer de classe"):
        ModifierEvaluation(depots).executer(ev.id, {**base, "classe_id": "c6"})
    assert ModifierEvaluation(depots).executer(ev.id, {**base, "libelle": "Interrogation 1"}).libelle == "Interrogation 1"


# ---------- Suppressions en cascade ----------
def test_cascades(depots):
    ev = evaluation(depots)
    EnregistrerNotes(depots).executer(ev.id, [{"eleve_id": "id1", "valeur": 12}, {"eleve_id": "id2", "valeur": 14}])

    assert SupprimerEleve(depots).executer("id2").notes_supprimees == 1
    ModifierEleve(depots).executer("id1", {"nom_prenoms": "Koné Awa", "classe_id": "c6"})  # change de classe
    assert LireEmploiDuTemps(depots).executer().notes == []

    ev2 = evaluation(depots, libelle="Devoir 1")
    ImporterEleves(depots).executer("c1", ["Bamba Issa"])
    eleve = [e for e in LireEmploiDuTemps(depots).executer().eleves if e.nom_prenoms == "Bamba Issa"][0]
    EnregistrerNotes(depots).executer(ev2.id, [{"eleve_id": eleve.id, "valeur": 10}])
    assert SupprimerEvaluation(depots).executer(ev2.id).notes_supprimees == 1

    EnregistrerNotes(depots).executer(ev.id, [{"eleve_id": eleve.id, "valeur": 11}])
    r = SupprimerClasse(depots).executer("c1")
    assert (r.evaluations_supprimees, r.notes_supprimees, r.eleves_supprimes) == (1, 1, 1)


def test_import_sauvegarde_avec_notes(depots):
    ev = evaluation(depots)
    EnregistrerNotes(depots).executer(ev.id, [{"eleve_id": "id1", "valeur": 12}])
    from dataclasses import asdict

    sauvegarde = asdict(LireEmploiDuTemps(depots).executer())
    edt = ImporterEmploiDuTemps(depots).executer(sauvegarde)
    assert len(edt.evaluations) == 1 and len(edt.notes) == 1

    sauvegarde["notes"].append(dict(sauvegarde["notes"][0], id="autre"))
    with pytest.raises(ErreurValidation, match="deux notes pour le même élève"):
        ImporterEmploiDuTemps(depots).executer(sauvegarde)
