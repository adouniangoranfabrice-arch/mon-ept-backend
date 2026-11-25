"""Vider la base (jours, heures, classes, séances) pour tout ressaisir depuis l'application.

Une sauvegarde JSON est d'abord écrite dans backend/sauvegardes/ (restaurable avec
scripts.importer ou le bouton « Importer »).
Usage (depuis backend/) :  .venv\\Scripts\\python -m scripts.vider [--oui]
"""
import json
import sys
from dataclasses import asdict
from datetime import datetime

from app.application.emploi_du_temps.lire_emploi_du_temps import LireEmploiDuTemps
from app.application.emploi_du_temps.vider_emploi_du_temps import ViderEmploiDuTemps
from app.config import BACKEND_DIR, get_settings
from app.infrastructure.stockage import ouvrir_stockage


def main() -> int:
    stockage = ouvrir_stockage(get_settings())
    stockage.preparer()
    edt = LireEmploiDuTemps(stockage.depots).executer()
    compte = {t: len(edt.liste(t)) for t in ("jours", "heures", "classes", "seances")}
    print(f"Stockage : {stockage.description}")
    print(f"Contenu actuel : {compte}")
    if not any(compte.values()):
        print("La base est déjà vide.")
        return 0

    dossier = BACKEND_DIR / "sauvegardes"
    dossier.mkdir(exist_ok=True)
    fichier = dossier / f"avant-vidage-{datetime.now():%Y-%m-%d_%H-%M-%S}.json"
    fichier.write_text(json.dumps(asdict(edt), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Sauvegarde : {fichier}")

    if "--oui" not in sys.argv and input("Tout supprimer ? (o/N) ").strip().lower() != "o":
        print("Annulé, rien n'a été supprimé.")
        return 1

    reste = ViderEmploiDuTemps(stockage.depots).executer()
    print(f"Base vidée : {{{', '.join(f'{t}: {len(reste.liste(t))}' for t in compte)}}}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
