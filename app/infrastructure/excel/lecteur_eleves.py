"""Implémentation du port LecteurListeEleves : fichiers .xlsx (openpyxl) et .csv.

Cherche, dans les 20 premières lignes de la première feuille, l'en-tête « Nom_prenoms »
(variantes acceptées : « Nom et prénoms », « NOMS ET PRENOMS », « Nom prénoms »…),
puis lit les noms en dessous. Accepte aussi deux colonnes « Nom » + « Prénoms »,
ou un fichier d'une seule colonne sans en-tête.
"""
import csv
import io
import re
import unicodedata
import zipfile

from openpyxl import load_workbook

from ...domain.errors import ErreurValidation

EN_TETES_NOM_PRENOMS = {
    "nomprenoms", "nomprenom", "nomsprenoms", "nometprenoms", "nometprenom", "nomsetprenoms",
    "nomcomplet", "nometprenomseleve", "nomsetprenomsdeleleve", "eleve", "eleves",
}
EN_TETES_NOM = {"nom", "noms"}
EN_TETES_PRENOMS = {"prenom", "prenoms"}
LIGNES_EN_TETE = 20


def _cle(valeur) -> str:
    """« Nom_Prénoms » → « nomprenoms »."""
    if valeur is None:
        return ""
    s = unicodedata.normalize("NFD", str(valeur))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z]", "", s)


def _texte(valeur) -> str:
    if valeur is None:
        return ""
    if isinstance(valeur, float) and valeur.is_integer():
        valeur = int(valeur)
    return re.sub(r"\s+", " ", str(valeur)).strip()


def _extraire(lignes: list[list]) -> list[str]:
    for i, ligne in enumerate(lignes[:LIGNES_EN_TETE]):
        cles = [_cle(v) for v in ligne]
        # 1) une colonne « Nom_prenoms »
        for j, cle in enumerate(cles):
            if cle in EN_TETES_NOM_PRENOMS:
                return [_texte(l[j]) for l in lignes[i + 1 :] if j < len(l)]
        # 2) deux colonnes « Nom » et « Prénoms »
        j_nom = next((j for j, c in enumerate(cles) if c in EN_TETES_NOM), None)
        j_pre = next((j for j, c in enumerate(cles) if c in EN_TETES_PRENOMS), None)
        if j_nom is not None and j_pre is not None:
            return [
                f"{_texte(l[j_nom]) if j_nom < len(l) else ''} {_texte(l[j_pre]) if j_pre < len(l) else ''}".strip()
                for l in lignes[i + 1 :]
            ]

    # 3) une seule colonne remplie, sans en-tête
    colonnes = {j for l in lignes for j, v in enumerate(l) if _texte(v)}
    if len(colonnes) == 1:
        j = colonnes.pop()
        return [_texte(l[j]) for l in lignes if j < len(l)]

    raise ErreurValidation(
        "Colonne « Nom_prenoms » introuvable. Ajoutez un en-tête « Nom_prenoms » au-dessus de la liste des élèves."
    )


def _lignes_xlsx(contenu: bytes) -> list[list]:
    try:
        classeur = load_workbook(io.BytesIO(contenu), read_only=True, data_only=True)
    except (zipfile.BadZipFile, KeyError, OSError, ValueError):
        raise ErreurValidation("Fichier Excel illisible. Enregistrez-le au format .xlsx et réessayez.") from None
    try:
        feuille = classeur.worksheets[0]
        return [list(l) for l in feuille.iter_rows(values_only=True)]
    finally:
        classeur.close()


def _lignes_csv(contenu: bytes) -> list[list]:
    for encodage in ("utf-8-sig", "cp1252"):
        try:
            texte = contenu.decode(encodage)
            break
        except UnicodeDecodeError:
            continue
    try:
        dialecte = csv.Sniffer().sniff(texte[:2048], delimiters=";,\t")
    except csv.Error:
        dialecte = csv.excel
    return [l for l in csv.reader(io.StringIO(texte), dialecte)]


class LecteurExcelEleves:
    def lire_noms(self, contenu: bytes, nom_fichier: str) -> list[str]:
        extension = nom_fichier.lower().rsplit(".", 1)[-1] if "." in nom_fichier else ""
        if extension == "xls":
            raise ErreurValidation("Format .xls (ancien Excel) non pris en charge : enregistrez le fichier en .xlsx.")
        if extension == "csv":
            lignes = _lignes_csv(contenu)
        elif extension in ("xlsx", "xlsm"):
            lignes = _lignes_xlsx(contenu)
        else:
            raise ErreurValidation("Choisissez un fichier Excel (.xlsx) ou CSV (.csv).")
        return [n for n in _extraire(lignes) if n]
