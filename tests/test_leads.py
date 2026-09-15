from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


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
