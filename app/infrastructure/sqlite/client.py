"""Connexion SQLite — sans effet de bord à l'import : rien n'est créé tant qu'on n'appelle pas ces fonctions."""
from pathlib import Path

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import sessionmaker


def creer_moteur(chemin: Path) -> Engine:
    moteur = create_engine(f"sqlite:///{chemin}", connect_args={"check_same_thread": False})

    @event.listens_for(moteur, "connect")
    def _activer_cles_etrangeres(dbapi_conn, _):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

    return moteur


def creer_fabrique_sessions(moteur: Engine) -> sessionmaker:
    return sessionmaker(bind=moteur, autoflush=False, expire_on_commit=False)
