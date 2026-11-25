"""Crée l'app, monte les routers, prépare la base au démarrage.

C'est le seul endroit qui connaît toutes les couches : il choisit les adaptateurs (MongoDB ou SQLite)
et les donne à l'API.

Lancer :  uvicorn app.main:app --reload   (depuis le dossier backend/)
Doc interactive : http://localhost:8000/docs
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from .api.errors import installer_gestionnaires_erreurs
from .api.routes import creer_routeur_api
from .application.emploi_du_temps.reinitialiser_emploi_du_temps import ReinitialiserEmploiDuTemps
from .config import Settings, get_settings
from .infrastructure.stockage import ouvrir_stockage

log = logging.getLogger("uvicorn.error")


def create_app(settings: Settings | None = None, client_mongo=None) -> FastAPI:
    """Stockage choisi par les Settings : MongoDB si MONGODB_URI est défini, sinon SQLite."""
    settings = settings or get_settings()
    stockage = ouvrir_stockage(settings, client_mongo)
    depots = stockage.depots

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        # Au démarrage : index / tables créés ; base vide remplie avec les données de départ
        if stockage.preparer():
            ReinitialiserEmploiDuTemps(depots).executer()
        log.info("Stockage : %s", stockage.description)
        yield

    app = FastAPI(title="Mon Emploi du Temps — API", version="3.0.0", lifespan=lifespan)
    app.state.depots = depots
    app.state.stockage = stockage.nom

    app.add_middleware(CORSMiddleware, allow_origins=list(settings.cors_origins), allow_methods=["*"], allow_headers=["*"])
    installer_gestionnaires_erreurs(app)
    app.include_router(creer_routeur_api())

    # En production : sert aussi le frontend compilé (npm run build → dist/)
    if settings.dist_dir.is_dir():
        app.mount("/", StaticFiles(directory=settings.dist_dir, html=True), name="frontend")
    else:

        @app.get("/", include_in_schema=False)
        def accueil():
            """Sans frontend compilé : la racine affiche la documentation de l'API."""
            return RedirectResponse("/docs")

    return app


app = create_app()
