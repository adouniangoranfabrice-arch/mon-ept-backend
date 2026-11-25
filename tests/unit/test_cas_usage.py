"""Cas d'usage testés avec les faux repositories en mémoire : ni SQLite, ni HTTP."""
import pytest

from app.application.classes.creer_classe import CreerClasse
from app.application.classes.lister_classes import ListerClasses
from app.application.classes.modifier_classe import ModifierClasse
from app.application.classes.supprimer_classe import SupprimerClasse
from app.application.classes.voir_classe import VoirClasse
from app.application.emploi_du_temps.importer_emploi_du_temps import ImporterEmploiDuTemps
from app.application.emploi_du_temps.reinitialiser_emploi_du_temps import ReinitialiserEmploiDuTemps
from app.application.seances.creer_seance import CreerSeance
from app.domain.errors import ErreurValidation, Introuvable

from .fakes import faux_depots


@pytest.fixture()
def depots():
    return faux_depots()


def test_creer_modifier_voir(depots):
    c = CreerClasse(depots).executer({"nom": "6e 1", "couleur": "#12B886"})
    assert c.id == "id1"
    ModifierClasse(depots).executer("id1", {"nom": "6e 1", "effectif": 40, "couleur": "#12B886"})
    assert VoirClasse(depots).executer("id1").effectif == 40
    assert [k.nom for k in ListerClasses(depots).executer()] == ["6e 1", "Tle D"]


def test_creer_refuse_doublon(depots):
    with pytest.raises(ErreurValidation, match="existe déjà"):
        CreerClasse(depots).executer({"nom": "TLE D", "couleur": "#000000"})


def test_supprimer_classe_supprime_ses_seances(depots):
    CreerSeance(depots).executer({"jour_id": "j1", "heure_id": "h1", "classe_id": "c1"})
    assert SupprimerClasse(depots).executer("c1").seances_supprimees == 1
    assert depots.emploi_du_temps.charger().seances == []
    with pytest.raises(Introuvable, match="Classe introuvable"):
        SupprimerClasse(depots).executer("c1")


def test_import_tout_ou_rien(depots):
    with pytest.raises(ErreurValidation, match=r"Import refusé \(classe n°1\)"):
        ImporterEmploiDuTemps(depots).executer({"classes": [{"nom": "", "couleur": "#000000"}]})
    assert len(depots.emploi_du_temps.charger().jours) == 7  # rien n'a changé

    with pytest.raises(ErreurValidation, match=r"Champ\(s\) manquant\(s\) pour classe : nom"):
        ImporterEmploiDuTemps(depots).executer({"classes": [{"couleur": "#000000"}]})


def test_reinitialiser():
    depots = faux_depots(edt=None)
    CreerClasse(depots).executer({"nom": "6e 1", "couleur": "#12B886"})
    edt = ReinitialiserEmploiDuTemps(depots).executer()
    assert [c.nom for c in edt.classes] == ["Tle D"]


def test_vider(depots):
    from app.application.emploi_du_temps.vider_emploi_du_temps import ViderEmploiDuTemps

    edt = ViderEmploiDuTemps(depots).executer()
    assert (edt.jours, edt.heures, edt.classes, edt.seances) == ([], [], [], [])
