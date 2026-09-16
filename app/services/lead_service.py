import logging
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.schemas.lead import LeadCreate
from app.services.qualification_service import QualificationResult

logger = logging.getLogger(__name__)


class LeadServiceError(Exception):
    """Raised when a database operation on a Lead record fails."""


def create_lead(db: Session, lead_data: LeadCreate) -> Lead:
    lead = Lead(
        name=lead_data.name,
        email=lead_data.email,
        phone=lead_data.phone,
    )
    try:
        db.add(lead)
        db.commit()
        db.refresh(lead)
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("database_operation_failed operation=create_lead error_type=%s", type(exc).__name__)
        raise LeadServiceError("Failed to create lead") from exc

    logger.info("lead_created lead_id=%s", lead.id)
    return lead


def get_lead(db: Session, lead_id: int) -> Optional[Lead]:
    try:
        return db.query(Lead).filter(Lead.id == lead_id).first()
    except SQLAlchemyError as exc:
        logger.error("database_operation_failed operation=get_lead error_type=%s", type(exc).__name__)
        raise LeadServiceError("Failed to retrieve lead") from exc


def save_qualified_lead(
    db: Session,
    *,
    session_id: str,
    lead_data: dict,
    booking_intent: bool,
    service_matches_clinic: bool,
    budget_is_suitable: bool,
    timeline_is_suitable: bool,
    conversation_summary: str,
    result: QualificationResult,
) -> Lead:
    """Create or update the Lead row for this chat session with the
    extracted lead data and the backend-computed qualification result."""
    try:
        lead = db.query(Lead).filter(Lead.session_id == session_id).first()
        if lead is None:
            lead = Lead(session_id=session_id)
            db.add(lead)

        lead.name = lead_data.get("name")
        lead.email = lead_data.get("email")
        lead.phone = lead_data.get("phone")
        lead.service = lead_data.get("service")
        lead.urgency = lead_data.get("urgency")
        lead.budget = lead_data.get("budget")
        lead.preferred_time = lead_data.get("preferred_time")
        lead.booking_intent = booking_intent
        lead.service_matches_clinic = service_matches_clinic
        lead.budget_is_suitable = budget_is_suitable
        lead.timeline_is_suitable = timeline_is_suitable
        lead.conversation_summary = conversation_summary
        lead.qualification_status = result.qualification_status
        lead.lead_score = result.lead_score

        db.commit()
        db.refresh(lead)
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(
            "database_operation_failed operation=save_qualified_lead error_type=%s", type(exc).__name__
        )
        raise LeadServiceError("Failed to save qualified lead") from exc

    return lead
