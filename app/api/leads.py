from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.lead import LeadCreate, LeadCreateResponse, LeadResponse
from app.services import lead_service
from app.services.lead_service import LeadServiceError

router = APIRouter()


@router.post("/api/leads", response_model=LeadCreateResponse)
def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    try:
        return lead_service.create_lead(db, lead)
    except LeadServiceError:
        raise HTTPException(status_code=500, detail="Failed to create lead. Please try again.")


@router.get("/api/leads/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    try:
        lead = lead_service.get_lead(db, lead_id)
    except LeadServiceError:
        raise HTTPException(status_code=500, detail="Failed to retrieve lead. Please try again.")
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead
