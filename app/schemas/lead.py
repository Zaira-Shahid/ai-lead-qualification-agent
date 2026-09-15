from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class LeadCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class LeadCreateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None


class LeadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    service: Optional[str] = None
    urgency: Optional[str] = None
    budget: Optional[float] = None
    preferred_time: Optional[str] = None
    location: Optional[str] = None
    booking_intent: Optional[bool] = None
    service_matches_clinic: Optional[bool] = None
    budget_is_suitable: Optional[bool] = None
    timeline_is_suitable: Optional[bool] = None
    qualification_status: Optional[str] = None
    lead_score: Optional[int] = None
    conversation_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime
