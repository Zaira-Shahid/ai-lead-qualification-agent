from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.sql import func

from app.database.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    service = Column(String, nullable=True)
    urgency = Column(String, nullable=True)
    budget = Column(Float, nullable=True)
    preferred_time = Column(String, nullable=True)
    location = Column(String, nullable=True)
    booking_intent = Column(Boolean, nullable=True)
    service_matches_clinic = Column(Boolean, nullable=True)
    budget_is_suitable = Column(Boolean, nullable=True)
    timeline_is_suitable = Column(Boolean, nullable=True)
    qualification_status = Column(String, nullable=True)
    lead_score = Column(Integer, nullable=True)
    conversation_summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
