import uuid

import pytest
from fastapi.testclient import TestClient

from app.api import qualify as qualify_module
from app.api.chat import _SESSIONS
from app.main import app
from app.models.lead import Lead
from tests.conftest import TestingSessionLocal

client = TestClient(app)


@pytest.fixture(autouse=True)
def _mock_notification_webhook_by_default(monkeypatch):
    """Avoid real network calls to N8N_WEBHOOK_URL in tests that don't care
    about the webhook itself. Tests that assert on the webhook call
    (test_qualify_sends_correct_payload_to_notification_webhook,
    test_qualify_succeeds_even_if_webhook_raises_unexpectedly) monkeypatch
    it again themselves, which simply overrides this default within that
    test."""
    monkeypatch.setattr(qualify_module.notification_service, "send_qualification_webhook", lambda payload: True)


def _make_session(**overrides):
    session_id = str(uuid.uuid4())
    session = {
        "messages": [],
        "lead": {
            "name": "Sarah",
            "email": "sarah@example.com",
            "phone": None,
            "service": "Cosmetic Dental Consultation",
            "urgency": "within_2_weeks",
            "budget": 500,
            "preferred_time": "afternoon",
        },
        "is_emergency": False,
        "booking_intent": True,
        "budget_is_suitable": True,
        "timeline_is_suitable": True,
        "conversation_summary": "Lead wants a cosmetic dental consultation.",
    }
    session.update(overrides)
    _SESSIONS[session_id] = session
    return session_id


def test_qualify_creates_lead_and_returns_qualified():
    session_id = _make_session()

    response = client.post("/api/qualify", json={"session_id": session_id})

    assert response.status_code == 200
    data = response.json()
    assert data["lead_score"] == 100
    assert data["qualification_status"] == "qualified"
    assert data["requires_human_review"] is False

    db = TestingSessionLocal()
    try:
        lead = db.query(Lead).filter(Lead.session_id == session_id).first()
        assert lead is not None
        assert lead.name == "Sarah"
        assert lead.email == "sarah@example.com"
        assert lead.service == "Cosmetic Dental Consultation"
        assert lead.qualification_status == "qualified"
        assert lead.lead_score == 100
        assert lead.service_matches_clinic is True
    finally:
        db.close()


def test_qualify_unknown_session_returns_404():
    response = client.post("/api/qualify", json={"session_id": "does-not-exist"})
    assert response.status_code == 404


def test_qualify_updates_existing_lead_on_repeated_call():
    session_id = _make_session(
        lead={
            "name": "John",
            "email": "john@example.com",
            "phone": None,
            "service": "Physiotherapy",
            "urgency": "asap",
            "budget": None,
            "preferred_time": None,
        },
        booking_intent=False,
        budget_is_suitable=False,
        timeline_is_suitable=False,
    )

    first = client.post("/api/qualify", json={"session_id": session_id})
    # valid_contact (10) + clear_service (20) + service_match (20) = 50
    assert first.json()["qualification_status"] == "needs_review"

    # Simulate the conversation continuing and improving the lead's info.
    _SESSIONS[session_id]["booking_intent"] = True
    _SESSIONS[session_id]["budget_is_suitable"] = True
    _SESSIONS[session_id]["timeline_is_suitable"] = True

    second = client.post("/api/qualify", json={"session_id": session_id})
    assert second.json()["qualification_status"] == "qualified"

    db = TestingSessionLocal()
    try:
        leads = db.query(Lead).filter(Lead.session_id == session_id).all()
        assert len(leads) == 1  # updated in place, not duplicated
        assert leads[0].qualification_status == "qualified"
    finally:
        db.close()


def test_qualify_sends_correct_payload_to_notification_webhook(monkeypatch):
    captured = {}

    def fake_send(payload):
        captured.update(payload)
        return True

    monkeypatch.setattr(qualify_module.notification_service, "send_qualification_webhook", fake_send)

    session_id = _make_session()
    response = client.post("/api/qualify", json={"session_id": session_id})

    assert response.status_code == 200
    assert captured["name"] == "Sarah"
    assert captured["email"] == "sarah@example.com"
    assert captured["service"] == "Cosmetic Dental Consultation"
    assert captured["lead_score"] == 100
    assert captured["qualification_status"] == "qualified"
    assert captured["requires_human_review"] is False
    assert "lead_id" in captured


def test_qualify_succeeds_even_if_webhook_raises_unexpectedly(monkeypatch):
    def raise_unexpected(payload):
        raise RuntimeError("simulated unexpected failure")

    monkeypatch.setattr(qualify_module.notification_service, "send_qualification_webhook", raise_unexpected)

    session_id = _make_session()
    response = client.post("/api/qualify", json={"session_id": session_id})

    assert response.status_code == 200
    data = response.json()
    assert data["qualification_status"] == "qualified"


def test_qualify_returns_500_on_database_failure(monkeypatch):
    from app.services.lead_service import LeadServiceError

    def raise_error(db, **kwargs):
        raise LeadServiceError("simulated failure")

    monkeypatch.setattr(qualify_module.lead_service, "save_qualified_lead", raise_error)

    session_id = _make_session()
    response = client.post("/api/qualify", json={"session_id": session_id})

    assert response.status_code == 500


def test_qualify_missing_required_info_downgrades_to_needs_review():
    session_id = _make_session(
        lead={
            "name": "Amelia",
            "email": "amelia@example.com",
            "phone": None,
            "service": "Skin Consultation",
            "urgency": None,
            "budget": None,
            "preferred_time": None,
        },
        booking_intent=True,
        budget_is_suitable=True,
        timeline_is_suitable=True,
    )

    response = client.post("/api/qualify", json={"session_id": session_id})
    data = response.json()
    assert data["qualification_status"] == "needs_review"
    assert data["requires_human_review"] is True
