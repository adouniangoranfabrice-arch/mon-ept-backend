"""Élèves : règles, cas d'usage (faux dépôts) et lecteur Excel réel (fichiers générés avec openpyxl)."""
import io

import pytest
from openpyxl import Workbook

from app.application.classes.supprimer_classe import SupprimerClasse
from app.application.eleves.creer_eleve import CreerEleve
from app.application.eleves.importer_eleves import ImporterEleves
from app.application.eleves.lire_fichier_eleves import LireFichierEleves
from app.application.eleves.lister_eleves import ListerEleves
from app.application.eleves.modifier_eleve import ModifierEleve
from app.domain.entities import Classe, EmploiDuTemps
from app.domain.errors import ErreurValidation, Introuvable
from app.infrastructure.excel.lecteur_eleves import LecteurExcelEleves

from .fakes import faux_depots


@pytest.fixture()
def depots():
    edt = EmploiDuTemps.par_defaut()
    edt.classes.append(Classe(id="c6", nom="6e 1", niveau="Sixième", couleur="#12B886"))
    return faux_depots(edt)


def xlsx(lignes: list[list]) -> bytes:
    wb = Workbook()
    for l in lignes:
        wb.active.append(l)
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()


# ---------- Règles et cas d'usage ----------
def test_creer_et_doublon_dans_la_classe(depots):
    CreerEleve(depots).executer({"nom_prenoms": "  KOUASSI   Aya Marie ", "classe_id": "c6"})
    with pytest.raises(ErreurValidation, match="déjà inscrit\\(e\\) en 6e 1"):
        CreerEleve(depots).executer({"nom_prenoms": "kouassi aya MARIE", "classe_id": "c6"})
    # même nom dans une autre classe : autorisé
    CreerEleve(depots).executer({"nom_prenoms": "Kouassi Aya Marie", "classe_id": "c1"})


def test_changer_de_classe(depots):
    e = CreerEleve(depots).executer({"nom_prenoms": "Yao Koffi", "classe_id": "c6"})
    assert ModifierEleve(depots).executer(e.id, {"nom_prenoms": "Yao Koffi", "classe_id": "c1"}).classe_id == "c1"
    with pytest.raises(ErreurValidation, match="Choisissez une classe"):
        ModifierEleve(depots).executer(e.id, {"nom_prenoms": "Yao Koffi", "classe_id": "inconnue"})


def test_apercu_puis_import(depots):
    apercu = LireFichierEleves(depots).executer("Yao Koffi\n\nKONÉ Awa\nKone Awa\n".encode(), "liste.xlsx")
    assert apercu.noms == ["Yao Koffi", "KONÉ Awa"] and apercu.doublons_fichier == 1

    CreerEleve(depots).executer({"nom_prenoms": "Yao Koffi", "classe_id": "c6"})
    r = ImporterEleves(depots).executer("c6", apercu.noms + ["Traoré Ali"])
    assert [e.nom_prenoms for e in r.ajoutes] == ["KONÉ Awa", "Traoré Ali"]
    assert r.ignores == ["Yao Koffi"]
    assert [e.nom_prenoms for e in ListerEleves(depots).executer()] == ["KONÉ Awa", "Traoré Ali", "Yao Koffi"]

    with pytest.raises(Introuvable):
        ImporterEleves(depots).executer("inconnue", ["X"])


def test_fichier_vide_ou_sans_eleve(depots):
    with pytest.raises(ErreurValidation, match="vide"):
        LireFichierEleves(depots).executer(b"", "a.xlsx")
    with pytest.raises(ErreurValidation, match="Aucun élève"):
        LireFichierEleves(depots).executer(b"\n  \n", "a.xlsx")


def test_supprimer_classe_supprime_ses_eleves(depots):
    ImporterEleves(depots).executer("c6", ["A B", "C D"])
    r = SupprimerClasse(depots).executer("c6")
    assert r.eleves_supprimes == 2 and depots.emploi_du_temps.charger().eleves == []


# ---------- Lecteur Excel réel ----------
lecteur = LecteurExcelEleves()


def test_excel_colonne_nom_prenoms_avec_titre_et_autres_colonnes():
    contenu = xlsx([
        ["LISTE DES ÉLÈVES — 6e 1"],
        [],
        ["N°", "Nom_prenoms", "Sexe"],
        [1, "KOUASSI Aya Marie", "F"],
        [2, None, None],
        [3, "  YAO   Koffi ", "M"],
    ])
    assert lecteur.lire_noms(contenu, "6e1.xlsx") == ["KOUASSI Aya Marie", "YAO Koffi"]


@pytest.mark.parametrize("en_tete", ["NOM ET PRÉNOMS", "Nom Prénoms", "noms_et_prenoms"])
def test_excel_variantes_d_en_tete(en_tete):
    assert lecteur.lire_noms(xlsx([[en_tete], ["Traoré Ali"]]), "l.xlsx") == ["Traoré Ali"]


def test_excel_colonnes_nom_et_prenoms_separees():
    assert lecteur.lire_noms(xlsx([["Nom", "Prénoms"], ["KONÉ", "Awa"]]), "l.xlsx") == ["KONÉ Awa"]


def test_excel_une_seule_colonne_sans_en_tete():
    assert lecteur.lire_noms(xlsx([["Yao Koffi"], ["Koné Awa"]]), "l.xlsx") == ["Yao Koffi", "Koné Awa"]


def test_csv_point_virgule_et_accents_windows():
    contenu = "Matricule;Nom_prenoms\n123;Koné Awa\n".encode("cp1252")
    assert lecteur.lire_noms(contenu, "liste.csv") == ["Koné Awa"]


def test_erreurs_de_fichier():
    with pytest.raises(ErreurValidation, match="introuvable"):
        lecteur.lire_noms(xlsx([["Matricule", "Sexe"], [1, "F"]]), "l.xlsx")
    with pytest.raises(ErreurValidation, match=r"\.xls"):
        lecteur.lire_noms(b"...", "ancien.xls")
    with pytest.raises(ErreurValidation, match="illisible"):
        lecteur.lire_noms(b"pas un excel", "faux.xlsx")
    with pytest.raises(ErreurValidation, match="Choisissez un fichier"):
        lecteur.lire_noms(b"...", "photo.png")
