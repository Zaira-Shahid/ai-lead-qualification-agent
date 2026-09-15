from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.lead import LeadCreate, LeadCreateResponse, LeadResponse
from app.services import lead_service

router = APIRouter()


@router.post("/api/leads", response_model=LeadCreateResponse)
def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    return lead_service.create_lead(db, lead)


@router.get("/api/leads/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = lead_service.get_lead(db, lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead
