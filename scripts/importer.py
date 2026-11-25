"""Importer un fichier JSON (remplace toutes les données, après validation).

Utilise le stockage configuré (MongoDB si MONGODB_URI est défini, sinon SQLite).
Usage (depuis backend/) :  .venv\\Scripts\\python -m scripts.importer fichier.json
"""
import json
import sys
from pathlib import Path

from app.application.emploi_du_temps.importer_emploi_du_temps import ImporterEmploiDuTemps
from app.config import get_settings
from app.domain.errors import ErreurDomaine
from app.infrastructure.stockage import ouvrir_stockage


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    try:
        donnees = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"Fichier illisible : {e}")
        return 1
    stockage = ouvrir_stockage(get_settings())
    stockage.preparer()
    try:
        edt = ImporterEmploiDuTemps(stockage.depots).executer(donnees)
    except ErreurDomaine as e:
        print(e.message)
        return 1
    print(f"Importé dans {stockage.description} : {len(edt.classes)} classes, {len(edt.seances)} séances.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
