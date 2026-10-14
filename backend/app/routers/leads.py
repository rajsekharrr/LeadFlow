"""
API router for lead-related endpoints.

Handles all HTTP routes for leads: listing, creating, retrieving, and updating.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud
from app.schemas import (
    CreateLeadRequest,
    UpdateLeadRequest,
    LeadResponse
)

router = APIRouter(
    prefix="/api/leads",
    tags=["leads"]
)


@router.get("", response_model=List[LeadResponse])
def list_leads(
    status: Optional[str] = Query(None, description="Filter by lead status"),
    search: Optional[str] = Query(None, description="Search by name or company"),
    db: Session = Depends(get_db)
):
    """
    Get all leads with optional filtering.

    Query Parameters:
    - status: Filter by status (e.g., "New", "Contacted", "Qualified")
    - search: Case-insensitive search on name or company fields

    Returns:
    - List of leads with computed fields (last_note, last_discussion_at, discussion_count)
    """
    leads = crud.get_leads(db, status=status, search=search)
    return leads


@router.post("", response_model=LeadResponse, status_code=201)
def create_lead(
    lead_data: CreateLeadRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new lead.

    Request Body:
    - name: Lead's full name (required)
    - company: Company name (optional)
    - phone: Phone number (optional)
    - status: Initial status (optional, defaults to "New")

    Returns:
    - Created lead with computed fields
    - HTTP 201 Created
    """
    lead = crud.create_lead(db, lead_data)
    return lead


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(
    lead_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a single lead by ID.

    Path Parameters:
    - lead_id: UUID of the lead

    Returns:
    - Lead with computed fields
    - HTTP 404 if lead not found

    Raises:
    - HTTPException 404: Lead not found
    """
    lead = crud.get_lead(db, lead_id)

    if lead is None:
        raise HTTPException(
            status_code=404,
            detail=f"Lead with id '{lead_id}' not found"
        )

    return lead


@router.patch("/{lead_id}", response_model=LeadResponse)
def update_lead(
    lead_id: str,
    update_data: UpdateLeadRequest,
    db: Session = Depends(get_db)
):
    """
    Update a lead's status or follow-up date.

    Path Parameters:
    - lead_id: UUID of the lead

    Request Body (all fields optional):
    - status: New status value
    - follow_up_at: New follow-up date/time

    Returns:
    - Updated lead with computed fields
    - HTTP 404 if lead not found

    Raises:
    - HTTPException 404: Lead not found
    """
    lead = crud.update_lead(db, lead_id, update_data)

    if lead is None:
        raise HTTPException(
            status_code=404,
            detail=f"Lead with id '{lead_id}' not found"
        )

    return lead
