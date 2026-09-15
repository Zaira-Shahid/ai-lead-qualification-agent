from typing import Optional

from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.schemas.lead import LeadCreate
from app.services.qualification_service import QualificationResult


def create_lead(db: Session, lead_data: LeadCreate) -> Lead:
    lead = Lead(
        name=lead_data.name,
        email=lead_data.email,
        phone=lead_data.phone,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def get_lead(db: Session, lead_id: int) -> Optional[Lead]:
    return db.query(Lead).filter(Lead.id == lead_id).first()


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
    return lead
