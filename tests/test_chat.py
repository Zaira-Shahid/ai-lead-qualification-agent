from fastapi.testclient import TestClient

from app.api import chat as chat_module
from app.main import app
from app.schemas.ai_response import AIResponse, ExtractedLead
from app.services.ai_service import AIServiceError

client = TestClient(app)


def _fake_ai_response(**overrides):
    defaults = dict(
        reply="Sure, what service are you interested in?",
        intent=None,
        lead=ExtractedLead(),
        missing_fields=[],
        booking_intent=False,
        service_matches_clinic=False,
        budget_is_suitable=False,
        timeline_is_suitable=False,
        conversation_summary="",
        is_emergency=False,
    )
    defaults.update(overrides)
    return AIResponse(**defaults)


def test_chat_collecting_information(monkeypatch):
    monkeypatch.setattr(
        chat_module,
        "get_ai_response",
        lambda messages: _fake_ai_response(lead=ExtractedLead(name="Sarah")),
    )

    response = client.post("/api/chat", json={"message": "I want a dental consultation"})

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "collecting_information"
    assert "session_id" in data


def test_chat_ready_for_qualification(monkeypatch):
    monkeypatch.setattr(
        chat_module,
        "get_ai_response",
        lambda messages: _fake_ai_response(
            lead=ExtractedLead(
                name="Sarah",
                email="sarah@example.com",
                service="Cosmetic Dental Consultation",
                urgency="within_2_weeks",
            )
        ),
    )

    response = client.post(
        "/api/chat", json={"session_id": "ready-session", "message": "Here is my info"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready_for_qualification"


def test_chat_emergency(monkeypatch):
    monkeypatch.setattr(
        chat_module,
        "get_ai_response",
        lambda messages: _fake_ai_response(
            reply="ignored by backend",
            is_emergency=True,
        ),
    )

    response = client.post(
        "/api/chat", json={"message": "I am having severe chest pain right now"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "emergency"
    assert "emergency" in data["reply"].lower() or "immediate" in data["reply"].lower()


def test_chat_ai_service_failure_returns_error_status(monkeypatch):
    def raise_error(messages):
        raise AIServiceError("boom")

    monkeypatch.setattr(chat_module, "get_ai_response", raise_error)

    response = client.post("/api/chat", json={"message": "hello"})

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"


def test_chat_session_accumulates_lead_data(monkeypatch):
    responses = [
        _fake_ai_response(lead=ExtractedLead(service="Physiotherapy")),
        _fake_ai_response(
            lead=ExtractedLead(email="john@example.com", urgency="asap")
        ),
    ]

    def fake_get_ai_response(messages):
        return responses.pop(0)

    monkeypatch.setattr(chat_module, "get_ai_response", fake_get_ai_response)

    first = client.post(
        "/api/chat", json={"session_id": "accum-session", "message": "I need physio"}
    )
    assert first.json()["status"] == "collecting_information"

    second = client.post(
        "/api/chat",
        json={"session_id": "accum-session", "message": "email is john@example.com, asap"},
    )
    assert second.json()["status"] == "ready_for_qualification"
