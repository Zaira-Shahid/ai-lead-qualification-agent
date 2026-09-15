import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///./test_leads.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True, scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("test_leads.db"):
        os.remove("test_leads.db")


def test_create_lead():
    response = client.post(
        "/api/leads",
        json={"name": "Sarah", "email": "sarah@example.com", "phone": "+123456789"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Sarah"
    assert data["email"] == "sarah@example.com"
    assert data["phone"] == "+123456789"
    assert "id" in data


def test_get_lead():
    create_response = client.post(
        "/api/leads",
        json={"name": "John", "email": "john@example.com"},
    )
    lead_id = create_response.json()["id"]

    response = client.get(f"/api/leads/{lead_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == lead_id
    assert data["name"] == "John"
    assert data["email"] == "john@example.com"
    assert data["phone"] is None
    assert data["qualification_status"] is None


def test_get_lead_not_found():
    response = client.get("/api/leads/999999")
    assert response.status_code == 404
