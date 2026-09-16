import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.schemas.lead import LeadCreate
from app.services import lead_service
from app.services.qualification_service import QualificationResult


class _FailingSession:
    """Minimal stand-in for a SQLAlchemy Session whose commit always fails,
    used to verify lead_service handles database failures without letting
    the exception escape unhandled."""

    def __init__(self):
        self.rolled_back = False
        self.added = []

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        raise SQLAlchemyError("simulated database failure")

    def rollback(self):
        self.rolled_back = True

    def refresh(self, obj):
        pass

    def query(self, *args, **kwargs):
        raise SQLAlchemyError("simulated database failure")


def test_create_lead_raises_lead_service_error_and_rolls_back_on_db_failure():
    db = _FailingSession()
    lead_data = LeadCreate(name="Sarah", email="sarah@example.com", phone=None)

    with pytest.raises(lead_service.LeadServiceError):
        lead_service.create_lead(db, lead_data)

    assert db.rolled_back is True


def test_get_lead_raises_lead_service_error_on_db_failure():
    db = _FailingSession()

    with pytest.raises(lead_service.LeadServiceError):
        lead_service.get_lead(db, 1)


def test_save_qualified_lead_raises_lead_service_error_on_db_failure():
    db = _FailingSession()
    result = QualificationResult(
        lead_score=85, qualification_status="qualified", requires_human_review=False
    )

    with pytest.raises(lead_service.LeadServiceError):
        lead_service.save_qualified_lead(
            db,
            session_id="abc123",
            lead_data={"name": "Sarah", "email": "sarah@example.com"},
            booking_intent=True,
            service_matches_clinic=True,
            budget_is_suitable=True,
            timeline_is_suitable=True,
            conversation_summary="",
            result=result,
        )
