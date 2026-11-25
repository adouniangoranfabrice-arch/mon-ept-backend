"""Routes testées de bout en bout (HTTP → cas d'usage → SQLite)."""


def test_donnees_de_depart(client):
    d = client.get("/api/data").json()
    assert len(d["jours"]) == 7
    assert len(d["heures"]) == 8
    assert [c["nom"] for c in d["classes"]] == ["Tle D"]
    assert d["seances"] == []
    assert d["eleves"] == [] and d["evaluations"] == [] and d["notes"] == []


def test_crud_classe(client):
    r = client.post("/api/classes", json={"nom": " 6e 1 ", "niveau": "Sixième", "effectif": "", "couleur": "#12B886"})
    assert r.status_code == 201, r.text
    c = r.json()
    assert c["nom"] == "6e 1" and c["effectif"] is None and c["id"]

    r = client.put(f"/api/classes/{c['id']}", json={**c, "effectif": "40"})
    assert r.json()["effectif"] == 40

    assert client.get(f"/api/classes/{c['id']}").json()["nom"] == "6e 1"
    assert client.delete(f"/api/classes/{c['id']}").json() == {
        "id": c["id"], "seances_supprimees": 0, "eleves_supprimes": 0, "evaluations_supprimees": 0, "notes_supprimees": 0,
    }
    assert client.get(f"/api/classes/{c['id']}").status_code == 404


def test_validations_en_francais(client):
    r = client.post("/api/classes", json={"nom": "tle d", "couleur": "#000000"})
    assert r.status_code == 400 and r.json()["detail"] == "La classe tle d existe déjà."

    r = client.post("/api/classes", json={"nom": "X", "effectif": "abc", "couleur": "#000000"})
    assert r.status_code == 422 and "Effectif" in r.json()["detail"]

    r = client.post("/api/heures", json={"code": "h9", "heure_debut": "08:00", "heure_fin": "09:00"})
    assert r.status_code == 400 and "chevauche H1" in r.json()["detail"]

    r = client.post("/api/heures", json={"code": "H9", "heure_debut": "19:00", "heure_fin": "18:30"})
    assert "après l'heure de début" in r.json()["detail"]

    r = client.post("/api/jours", json={"libelle": "Lundi bis", "ordre": 1})
    assert r.json()["detail"] == "L'ordre 1 est déjà utilisé."


def test_seance_conflit_et_cascade(client):
    s = {"jour_id": "j1", "heure_id": "h1", "classe_id": "c1", "salle": "B12"}
    assert client.post("/api/seances", json=s).status_code == 201

    r = client.post("/api/seances", json=s)
    assert r.status_code == 400 and r.json()["detail"] == "Ce créneau est déjà pris par Tle D."

    r = client.post("/api/seances", json={**s, "classe_id": "inconnue", "heure_id": "h2"})
    assert r.json()["detail"] == "Choisissez une classe."

    assert client.delete("/api/classes/c1").json()["seances_supprimees"] == 1
    assert client.get("/api/seances").json() == []


def test_donnees_ordonnees(client):
    for nom in ["Tle D2", "2nde C", "6e 10", "6e 2", "1ère A", "3e 1"]:
        client.post("/api/classes", json={"nom": nom, "couleur": "#000000"})
    noms = [c["nom"] for c in client.get("/api/classes").json()]
    assert noms == ["6e 2", "6e 10", "3e 1", "2nde C", "1ère A", "Tle D", "Tle D2"]

    for j, h in [("j4", "h1"), ("j1", "h3"), ("j1", "h1")]:
        client.post("/api/seances", json={"jour_id": j, "heure_id": h, "classe_id": "c1"})
    creneaux = [(s["jour_id"], s["heure_id"]) for s in client.get("/api/seances").json()]
    assert creneaux == [("j1", "h1"), ("j1", "h3"), ("j4", "h1")]


def test_health_indique_le_stockage(client, app):
    assert client.get("/api/health").json() == {"status": "ok", "stockage": app.state.stockage}


def test_racine(client):
    assert client.get("/", follow_redirects=False).status_code in (200, 307)  # 200 si dist/ existe


def test_import(client):
    d = client.get("/api/data").json()
    d["classes"].append({"id": "c2", "nom": "6e 1", "niveau": "Sixième", "effectif": None, "couleur": "#12B886"})
    d["seances"].append({"id": "s1", "jour_id": "j2", "heure_id": "h3", "classe_id": "c2", "salle": "", "recurrente": True})
    r = client.put("/api/data", json=d)
    assert r.status_code == 200, r.text
    assert len(r.json()["seances"]) == 1

    mauvais = {**d, "classes": [{"id": "c3", "couleur": "#000000"}]}
    r = client.put("/api/data", json=mauvais)
    assert r.status_code == 400 and "Import refusé (classe n°1)" in r.json()["detail"]
    assert len(client.get("/api/classes").json()) == 2  # rien n'a changé

    assert client.put("/api/data", json={"jours": []}).status_code == 422


def test_base_videe_reste_vide_au_redemarrage(app):
    """Après un vidage volontaire, le redémarrage ne remet PAS les données de départ."""
    from fastapi.testclient import TestClient

    from app.application.emploi_du_temps.vider_emploi_du_temps import ViderEmploiDuTemps

    with TestClient(app) as c:
        ViderEmploiDuTemps(app.state.depots).executer()
    with TestClient(app) as c:  # nouveau démarrage (lifespan rejoué)
        assert c.get("/api/data").json() == {"jours": [], "heures": [], "classes": [], "eleves": [], "evaluations": [], "notes": [], "seances": []}
        r = c.post("/api/jours", json={"libelle": "Lundi", "ordre": 1})
        assert r.status_code == 201, r.text


def test_eleves_import_excel_de_bout_en_bout(client):
    """Fichier Excel envoyé → aperçu → import dans une classe → suppression de la classe."""
    import io

    from openpyxl import Workbook

    wb = Workbook()
    for ligne in (["N°", "Nom_prenoms"], [1, "KOUASSI Aya"], [2, "Yao Koffi"], [3, "yao  koffi"]):
        wb.active.append(ligne)
    fichier = io.BytesIO()
    wb.save(fichier)

    r = client.post("/api/eleves/lecture", files={"fichier": ("6e1.xlsx", fichier.getvalue())})
    assert r.status_code == 200, r.text
    assert r.json() == {"noms": ["KOUASSI Aya", "Yao Koffi"], "doublons_fichier": 1}

    r = client.post("/api/eleves/import", json={"classe_id": "c1", "noms": r.json()["noms"]})
    assert r.status_code == 200, r.text
    assert len(r.json()["ajoutes"]) == 2 and r.json()["ignores"] == []

    r = client.post("/api/eleves/import", json={"classe_id": "c1", "noms": ["Yao Koffi", "Traoré Ali"]})
    assert [e["nom_prenoms"] for e in r.json()["ajoutes"]] == ["Traoré Ali"] and r.json()["ignores"] == ["Yao Koffi"]
    assert len(client.get("/api/data").json()["eleves"]) == 3

    r = client.post("/api/eleves/lecture", files={"fichier": ("liste.xls", b"...")})
    assert r.status_code == 400 and ".xlsx" in r.json()["detail"]

    assert client.delete("/api/classes/c1").json()["eleves_supprimes"] == 3
    assert client.get("/api/eleves").json() == []


def test_eleve_crud(client):
    r = client.post("/api/eleves", json={"nom_prenoms": "Koné Awa", "classe_id": "c1"})
    assert r.status_code == 201, r.text
    e = r.json()
    assert client.post("/api/eleves", json={"nom_prenoms": "KONE awa", "classe_id": "c1"}).json()["detail"] == "« KONE awa » est déjà inscrit(e) en Tle D."
    r = client.put(f"/api/eleves/{e['id']}", json={"nom_prenoms": "Koné Awa Marie", "classe_id": "c1"})
    assert r.json()["nom_prenoms"] == "Koné Awa Marie"
    assert client.delete(f"/api/eleves/{e['id']}").status_code == 200
    assert client.get(f"/api/eleves/{e['id']}").status_code == 404


def test_notes_de_bout_en_bout(client):
    """Évaluation → saisie des notes → modification → suppression de la classe."""
    ajoutes = client.post("/api/eleves/import", json={"classe_id": "c1", "noms": ["Koné Awa", "Yao Koffi"]}).json()["ajoutes"]
    awa, koffi = (e["id"] for e in ajoutes)

    r = client.post("/api/evaluations", json={"classe_id": "c1", "trimestre": 1, "libelle": "Interro 1", "date": "2026-10-02", "bareme": 10})
    assert r.status_code == 201, r.text
    ev = r.json()

    r = client.put(f"/api/evaluations/{ev['id']}/notes", json={"notes": [{"eleve_id": awa, "valeur": 7.5}, {"eleve_id": koffi, "valeur": None}]})
    assert r.status_code == 200, r.text
    assert [(n["eleve_id"], n["valeur"]) for n in r.json()] == [(awa, 7.5)]

    r = client.put(f"/api/evaluations/{ev['id']}/notes", json={"notes": [{"eleve_id": awa, "valeur": 11}]})
    assert r.status_code == 400 and r.json()["detail"] == "Note de Koné Awa : elle doit être comprise entre 0 et 10."

    d = client.get("/api/data").json()
    assert len(d["evaluations"]) == 1 and [n["valeur"] for n in d["notes"]] == [7.5]

    r = client.delete("/api/classes/c1").json()
    assert (r["evaluations_supprimees"], r["notes_supprimees"], r["eleves_supprimes"]) == (1, 1, 2)
