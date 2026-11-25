"""Application complète, testée avec CHAQUE stockage : SQLite (fichier de test) et MongoDB (mongomock).

Jamais votre edt.db ni votre vraie base MongoDB.
"""
import mongomock
import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


@pytest.fixture(scope="session", params=["sqlite", "mongodb"])
def app(request, tmp_path_factory):
    if request.param == "sqlite":
        db = tmp_path_factory.mktemp("db") / "test.db"
        return create_app(Settings(db_path=db, stockage_force="sqlite"))
    return create_app(Settings(stockage_force="mongodb", mongodb_db="edt_test"), client_mongo=mongomock.MongoClient())


@pytest.fixture()
def client(app):
    with TestClient(app) as c:
        c.post("/api/reset")
        yield c
