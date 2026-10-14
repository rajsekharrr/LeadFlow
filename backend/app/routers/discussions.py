"""
API router for discussion-related endpoints.

Handles all HTTP routes for discussions: listing and creating.
Discussions are always associated with a parent lead.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud
from app.schemas import (
    CreateDiscussionRequest,
    DiscussionResponse
)

router = APIRouter(
    prefix="/api/leads",
    tags=["discussions"]
)


@router.get("/{lead_id}/discussions", response_model=List[DiscussionResponse])
def list_discussions(
    lead_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all discussions for a lead.

    Path Parameters:
    - lead_id: UUID of the parent lead

    Returns:
    - List of discussions in reverse chronological order (most recent first)
    - Empty list if lead has no discussions
    - HTTP 404 if lead not found

    Raises:
    - HTTPException 404: Lead not found
    """
    # First verify the lead exists
    lead = crud.get_lead(db, lead_id)
    if lead is None:
        raise HTTPException(
            status_code=404,
            detail=f"Lead with id '{lead_id}' not found"
        )

    # Get discussions for the lead
    discussions = crud.get_discussions(db, lead_id)
    return discussions


@router.post("/{lead_id}/discussions", response_model=DiscussionResponse, status_code=201)
def create_discussion(
    lead_id: str,
    discussion_data: CreateDiscussionRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new discussion for a lead.

    IMPORTANT: If the discussion includes a follow_up_at, the parent lead's
    follow_up_at and updated_at are also updated in the same transaction.

    Path Parameters:
    - lead_id: UUID of the parent lead

    Request Body:
    - note: Discussion content (required)
    - follow_up_at: Optional follow-up date/time (also updates parent lead)

    Returns:
    - Created discussion
    - HTTP 201 Created
    - HTTP 404 if lead not found

    Raises:
    - HTTPException 404: Lead not found
    """
    discussion = crud.create_discussion(db, lead_id, discussion_data)

    if discussion is None:
        raise HTTPException(
            status_code=404,
            detail=f"Lead with id '{lead_id}' not found"
        )

    return discussion
