import logging
import uuid
from typing import Dict, List, Literal, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ai_service import AIServiceError, get_ai_response

logger = logging.getLogger(__name__)

router = APIRouter()

EMERGENCY_REPLY = (
    "I'm sorry you're experiencing this. This assistant cannot handle medical "
    "emergencies. Please contact your local emergency service or seek immediate "
    "medical attention."
)

ERROR_REPLY = (
    "Sorry, something went wrong on our end. Please try again in a moment, or "
    "contact NovaCare Clinic directly if this continues."
)


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    status: Literal["collecting_information", "ready_for_qualification", "emergency", "error"]


# In-memory conversation session store. Each session holds the chat history
# (for AI context) and the lead fields extracted so far. This does not
# persist across process restarts; qualification results are persisted to
# the Lead database separately, in a later phase.
_SESSIONS: Dict[str, dict] = {}


def _new_session() -> dict:
    return {
        "messages": [],
        "lead": {},
        "is_emergency": False,
    }


def _merge_lead_data(session_lead: dict, extracted: dict) -> None:
    for key, value in extracted.items():
        if value is not None:
            session_lead[key] = value


def _required_info_complete(session_lead: dict) -> bool:
    has_service = bool(session_lead.get("service"))
    has_contact = bool(session_lead.get("email") or session_lead.get("phone"))
    has_urgency = bool(session_lead.get("urgency"))
    return has_service and has_contact and has_urgency


@router.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    session = _SESSIONS.setdefault(session_id, _new_session())

    session["messages"].append({"role": "user", "content": request.message})

    try:
        ai_response = get_ai_response(session["messages"])
    except AIServiceError:
        logger.error("chat_ai_service_failed session_id=%s", session_id)
        return ChatResponse(reply=ERROR_REPLY, session_id=session_id, status="error")

    session["messages"].append({"role": "assistant", "content": ai_response.reply})
    _merge_lead_data(session["lead"], ai_response.lead.model_dump())

    if ai_response.is_emergency:
        session["is_emergency"] = True
        logger.info("chat_emergency_detected session_id=%s", session_id)
        return ChatResponse(reply=EMERGENCY_REPLY, session_id=session_id, status="emergency")

    status: Literal["collecting_information", "ready_for_qualification"] = (
        "ready_for_qualification" if _required_info_complete(session["lead"]) else "collecting_information"
    )

    return ChatResponse(reply=ai_response.reply, session_id=session_id, status=status)
