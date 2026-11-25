"""Règles métier des entités : pures, sans base ni serveur."""
import pytest

from app.domain.entities import Classe, EmploiDuTemps, Heure, Seance
from app.domain.errors import ErreurValidation


def test_normaliser_classe():
    c = Classe(id=None, nom="  6e 1 ", niveau=None, couleur=" #12B886 ").normalise()
    assert (c.nom, c.niveau, c.couleur) == ("6e 1", "", "#12B886")


def test_heure_qui_chevauche():
    h = Heure(id=None, code="h9", heure_debut="08:00", heure_fin="09:00").normalise()
    assert h.erreur(EmploiDuTemps.par_defaut()) == "Ce créneau chevauche H1 (07:30 – 08:30)."


def test_seance_sur_creneau_pris():
    edt = EmploiDuTemps.par_defaut()
    edt.seances.append(Seance(id="s1", jour_id="j1", heure_id="h1", classe_id="c1"))
    with pytest.raises(ErreurValidation, match="Ce créneau est déjà pris par Tle D."):
        edt.verifier(Seance(id=None, jour_id="j1", heure_id="h1", classe_id="c1"))


def test_tri_des_classes_de_la_6e_a_la_tle():
    noms = ["Tle D", "2nde A2", "6e 10", "6e 2", "1ère A", "Seconde B", "3e 1"]
    edt = EmploiDuTemps(classes=[Classe(id=n, nom=n, couleur="#000000") for n in noms])
    assert [c.nom for c in edt.trie().classes] == ["6e 2", "6e 10", "3e 1", "2nde A2", "Seconde B", "1ère A", "Tle D"]
    assert Classe(id=None, nom="Club info", niveau="Première").rang == 5
