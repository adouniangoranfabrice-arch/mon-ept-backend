# Mon Emploi du Temps — Backend

API **FastAPI** de l'application « Mon Emploi du Temps » (prof d'informatique) :
jours, créneaux horaires, classes, séances, élèves (import Excel), évaluations et notes par trimestre.

- Python 3.11+, FastAPI, Pydantic v2
- Stockage **MongoDB** (Atlas ou local) ou **SQLite**, au choix
- Clean Architecture : le métier ne dépend ni de FastAPI ni de la base

---

## Démarrage rapide

Depuis le dossier `backend/` :

```bash
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt     # première fois seulement
copy .env.example .env                                      # puis renseignez MONGODB_URI (facultatif)
.venv\Scripts\python -m uvicorn app.main:app --reload
```

| Adresse | Contenu |
|---|---|
| http://localhost:8000/docs | Documentation interactive (tester les routes) |
| http://localhost:8000/api/health | État du serveur et stockage utilisé |
| http://localhost:8000 | L'application, si le frontend est compilé (`frontend/dist`), sinon redirection vers `/docs` |

Le frontend en développement (`npm run dev`, port 5173) envoie ses appels `/api` à ce serveur.

---

## Configuration (`backend/.env`)

| Variable | Rôle | Défaut |
|---|---|---|
| `MONGODB_URI` | Adresse MongoDB. **Si elle est définie, MongoDB est utilisé** | vide → SQLite |
| `MONGODB_DB` | Nom de la base MongoDB | `emploi_du_temps` |
| `EDT_STOCKAGE` | Forcer `mongodb` ou `sqlite` | déduit de `MONGODB_URI` |
| `EDT_DB_PATH` | Fichier SQLite | `backend/edt.db` |
| `EDT_DIST_DIR` | Frontend compilé servi par le backend | `../frontend/dist` |

Les variables d'environnement du système sont prioritaires sur le fichier `.env`.

> `.env` contient le mot de passe MongoDB : il est exclu de git (`.gitignore`). Ne le partagez pas.
> Avec MongoDB Atlas, l'adresse IP du poste doit être autorisée (*Network Access*).

### Stockage

- **MongoDB** : collections `jours`, `heures`, `classes`, `eleves`, `evaluations`, `notes`, `seances`
  (l'id de chaque élément est le `_id`). Les index sont créés au démarrage :
  un seul cours par jour + heure (`uq_seance_creneau`), une seule note par élève et par évaluation (`uq_note_eleve`)…
  Une base vidée volontairement n'est pas re-remplie avec les données de départ.
- **SQLite** : fichier `edt.db`, créé au premier démarrage avec les données de départ.

Les deux implémentent les mêmes ports : l'API se comporte de la même façon quel que soit le stockage.

---

## API

Toutes les routes sont préfixées par `/api`. Les erreurs renvoient `{"detail": "message en français"}`.

| Code | Signification |
|---|---|
| 400 | Règle métier non respectée (créneau déjà pris, note hors barème…) |
| 404 | Élément introuvable |
| 409 | Conflit d'unicité en base |
| 422 | Donnée mal formée (champ manquant, mauvais type) |

### Données globales

| Méthode | Route | Rôle |
|---|---|---|
| GET | `/api/health` | Le serveur répond-il ? Quel stockage ? |
| GET | `/api/data` | Toutes les données |
| PUT | `/api/data` | Remplacer toutes les données (import d'une sauvegarde, entièrement validé avant écriture) |
| POST | `/api/reset` | Revenir aux données de départ |

### CRUD

| Méthode | Route | Rôle |
|---|---|---|
| GET / POST | `/api/{table}` | Lister / créer |
| GET / PUT / DELETE | `/api/{table}/{id}` | Voir / modifier / supprimer |

`{table}` = `jours`, `heures`, `classes`, `seances`, `eleves`, `evaluations`.

Une suppression renvoie ce qui a été supprimé en cascade :

```json
{ "id": "…", "seances_supprimees": 3, "eleves_supprimes": 0, "evaluations_supprimees": 0, "notes_supprimees": 0 }
```

### Élèves (import Excel)

| Méthode | Route | Rôle |
|---|---|---|
| POST | `/api/eleves/lecture` | Envoi d'un fichier `.xlsx` / `.csv` (multipart, champ `fichier`) → aperçu des noms, **rien n'est enregistré** |
| POST | `/api/eleves/import` | `{ "classe_id": "…", "noms": ["…"] }` → inscrit les élèves dans la classe |

Le fichier doit contenir une colonne **Nom_prenoms** (aussi reconnus : « Nom et prénoms »,
« NOMS ET PRÉNOMS », ou deux colonnes « Nom » + « Prénoms »). Les doublons et les élèves déjà
inscrits sont ignorés (comparaison sans accents ni majuscules). Un ancien `.xls` doit être réenregistré en `.xlsx`.

### Notes

| Méthode | Route | Rôle |
|---|---|---|
| PUT | `/api/evaluations/{id}/notes` | Remplace toutes les notes de l'évaluation |

```json
{ "notes": [ { "eleve_id": "…", "valeur": 12.5 }, { "eleve_id": "…", "valeur": null } ] }
```

`null` = pas de note (absent). L'enregistrement est **tout ou rien** : une seule note invalide et rien n'est écrit.

---

## Règles métier

| Élément | Règles |
|---|---|
| Jour | Libellé et ordre uniques (1 = lundi … 7 = dimanche), interrupteur « actif » |
| Heure | Format `HH:MM`, fin après le début, pas de chevauchement entre créneaux |
| Classe | Nom unique, niveau de la 6e à la Terminale, couleur ; triées de la 6e à la Tle D |
| Séance | Un seul cours par jour + heure |
| Élève | Pas deux fois le même nom dans une classe |
| Évaluation | Trimestre 1, 2 ou 3 ; barème 1–100 (20 par défaut) ; coefficient 0–10 (1 par défaut) ; libellé unique par classe et trimestre |
| Note | Entre 0 et le barème ; uniquement pour un élève de la classe de l'évaluation ; une note par élève et par évaluation |

- **Moyenne du trimestre** (sur 20) = Σ (note / barème × 20 × coefficient) / Σ coefficients, arrondie à 2 décimales.
- **Moyenne annuelle** = moyenne des trimestres qui ont une moyenne.
- Une évaluation déjà notée ne peut ni changer de classe, ni avoir un barème inférieur à la meilleure note.

**Suppressions en cascade**

| On supprime… | … ce qui part avec |
|---|---|
| Un jour ou une heure | Ses séances |
| Une classe | Ses séances, ses élèves, ses évaluations et leurs notes |
| Un élève | Ses notes (aussi s'il **change de classe**) |
| Une évaluation | Ses notes |

---

## Scripts

Depuis `backend/` :

```bash
.venv\Scripts\python -m scripts.exporter sauvegarde.json   # copie de la base en JSON
.venv\Scripts\python -m scripts.importer sauvegarde.json   # remplace la base (après validation)
.venv\Scripts\python -m scripts.vider                       # sauvegarde dans sauvegardes/, puis vide la base
```

Les sauvegardes JSON ont le même format que `GET /api/data` ; les anciennes (sans élèves ni notes) restent importables.

---

## Tests

```bash
.venv\Scripts\python -m pytest -q
```

- `tests/unit/` : entités, cas d'usage (faux dépôts en mémoire) et respect de l'architecture.
- `tests/integration/` : toutes les routes, exécutées **deux fois** : avec SQLite et avec MongoDB (mongomock).
  Aucune base réelle n'est touchée.

---

## Architecture (Clean Architecture)

Les dépendances vont toujours **vers le domaine** : `api` et `infrastructure` → `application` → `domain`.
Le test `tests/unit/test_architecture.py` échoue si cette règle est violée.

```
backend/
├── app/
│   ├── main.py                     # crée l'app, monte les routes, prépare la base au démarrage
│   ├── config.py                   # Settings lus dans l'environnement et backend/.env
│   │
│   ├── domain/                     # ❶ CŒUR : aucune dépendance externe
│   │   ├── entities/               #    jour, heure, classe, eleve, evaluation, note, seance,
│   │   │                           #    emploi_du_temps (verifier(), trie(), par_defaut())
│   │   ├── ports/
│   │   │   ├── repositories.py     #    interfaces des dépôts + Depots (regroupe tous les ports)
│   │   │   ├── fichiers.py         #    LecteurListeEleves (lecture du fichier Excel)
│   │   │   └── identifiants.py     #    GenerateurId
│   │   └── errors.py               #    ErreurValidation, Introuvable, Conflit
│   │
│   ├── application/                # ❷ CAS D'USAGE : un fichier = une action
│   │   ├── commun/crud.py          #    comportement commun (lister, voir, créer, modifier, supprimer)
│   │   ├── jours/  heures/  classes/  seances/  eleves/  evaluations/
│   │   ├── notes/                  #    enregistrer_notes
│   │   └── emploi_du_temps/        #    lire, importer, réinitialiser, vider
│   │
│   ├── infrastructure/             # ❸ ADAPTATEURS : implémentent les ports
│   │   ├── mongo/                  #    client, indexes, fabrique, repositories/
│   │   ├── sqlite/                 #    client, modeles (SQLAlchemy), schema, fabrique, repositories/
│   │   ├── excel/lecteur_eleves.py #    .xlsx (openpyxl) et .csv
│   │   ├── stockage.py             #    choisit MongoDB ou SQLite selon la configuration
│   │   └── identifiants.py         #    generer_uuid
│   │
│   └── api/                        # ❹ PRÉSENTATION HTTP
│       ├── dependencies.py         #    injection des cas d'usage : cas_usage(CreerClasse)
│       ├── errors.py               #    erreurs du domaine → 400 / 404 / 409 / 422
│       ├── schemas/                #    DTO Pydantic d'entrée (…In) et de sortie (…Out)
│       └── routes/                 #    une route = un cas d'usage
│
├── scripts/                        # exporter, importer, vider
├── tests/
│   ├── unit/
│   └── integration/
├── requirements.txt
├── .env.example                    # modèle de configuration
└── .env                            # votre configuration (non versionnée)
```

### Ajouter une fonctionnalité

1. **Domaine** : l'entité et ses règles dans `domain/entities/`, l'interface du dépôt dans `domain/ports/`.
2. **Application** : un fichier par action dans `application/<fonctionnalité>/`.
3. **Infrastructure** : le dépôt MongoDB **et** le dépôt SQLite, ajoutés aux deux `fabrique.py`.
4. **API** : les schémas dans `api/schemas/`, la route dans `api/routes/` (déclarée dans `routes/__init__.py`).
5. **Tests** : unitaires avec les faux dépôts (`tests/unit/fakes.py`), intégration dans `tests/integration/`.
