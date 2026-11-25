"""Exporter les données dans un fichier JSON (même format que le bouton « Exporter »).

Utilise le stockage configuré (MongoDB si MONGODB_URI est défini, sinon SQLite).
Usage (depuis backend/) :  .venv\\Scripts\\python -m scripts.exporter [fichier.json]
"""
import json
import sys
from dataclasses import asdict
from datetime import date
from pathlib import Path

from app.application.emploi_du_temps.lire_emploi_du_temps import LireEmploiDuTemps
from app.config import get_settings
from app.infrastructure.stockage import ouvrir_stockage


def main() -> int:
    cible = Path(sys.argv[1] if len(sys.argv) > 1 else f"emploi-du-temps-{date.today()}.json")
    stockage = ouvrir_stockage(get_settings())
    stockage.preparer()
    edt = LireEmploiDuTemps(stockage.depots).executer()
    cible.write_text(json.dumps(asdict(edt), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Exporté depuis {stockage.description} : {cible.resolve()} ({len(edt.classes)} classes, {len(edt.seances)} séances)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
