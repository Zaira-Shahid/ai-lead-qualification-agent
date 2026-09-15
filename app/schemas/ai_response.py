from typing import List, Optional

from pydantic import BaseModel


class ExtractedLead(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    service: Optional[str] = None
    urgency: Optional[str] = None
    budget: Optional[float] = None
    preferred_time: Optional[str] = None


class AIResponse(BaseModel):
    reply: str
    intent: Optional[str] = None
    lead: ExtractedLead
    missing_fields: List[str] = []
    booking_intent: bool = False
    service_matches_clinic: bool = False
    budget_is_suitable: bool = False
    timeline_is_suitable: bool = False
    conversation_summary: str = ""
    is_emergency: bool = False
