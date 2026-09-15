import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.chat import _SESSIONS
from app.database.database import get_db
from app.services import lead_service
from app.services.qualification_service import qualify_lead, service_matches_clinic_offering

logger = logging.getLogger(__name__)

router = APIRouter()


class QualifyRequest(BaseModel):
    session_id: str


class QualifyResponse(BaseModel):
    lead_score: int
    qualification_status: str
    requires_human_review: bool


@router.post("/api/qualify", response_model=QualifyResponse)
def qualify(request: QualifyRequest, db: Session = Depends(get_db)):
    session = _SESSIONS.get(request.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    logger.info("qualification_started session_id=%s", request.session_id)

    lead_data = session["lead"]

    result = qualify_lead(
        email=lead_data.get("email"),
        phone=lead_data.get("phone"),
        service=lead_data.get("service"),
        urgency=lead_data.get("urgency"),
        booking_intent=session.get("booking_intent", False),
        budget_is_suitable=session.get("budget_is_suitable", False),
        timeline_is_suitable=session.get("timeline_is_suitable", False),
    )

    lead_service.save_qualified_lead(
        db,
        session_id=request.session_id,
        lead_data=lead_data,
        booking_intent=session.get("booking_intent", False),
        service_matches_clinic=service_matches_clinic_offering(lead_data.get("service")),
        budget_is_suitable=session.get("budget_is_suitable", False),
        timeline_is_suitable=session.get("timeline_is_suitable", False),
        conversation_summary=session.get("conversation_summary", ""),
        result=result,
    )

    logger.info(
        "qualification_completed session_id=%s status=%s", request.session_id, result.qualification_status
    )

    return QualifyResponse(
        lead_score=result.lead_score,
        qualification_status=result.qualification_status,
        requires_human_review=result.requires_human_review,
    )
