"""
CRUD (Create, Read, Update, Delete) operations for LeadFlow.

This module contains all database access logic, implementing the repository
pattern. Route handlers call these functions rather than writing queries
directly, keeping the data layer independently testable.
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc

from app.models import Lead, Discussion
from app.schemas import (
    CreateLeadRequest,
    UpdateLeadRequest,
    CreateDiscussionRequest
)


# ==================== Lead CRUD Operations ====================

def get_leads(
    db: Session,
    status: Optional[str] = None,
    search: Optional[str] = None
) -> List[Lead]:
    """
    Get all leads with optional filtering.

    Args:
        db: Database session
        status: Optional status filter (e.g., "New", "Contacted")
        search: Optional search string (matches name or company, case-insensitive)

    Returns:
        List of Lead objects with computed fields attached:
        - last_note: Most recent discussion note
        - last_discussion_at: Timestamp of most recent discussion
        - discussion_count: Total number of discussions
    """
    # Start with base query
    query = db.query(Lead)

    # Apply status filter if provided
    if status:
        query = query.filter(Lead.status == status)

    # Apply search filter if provided
    # ilike() is case-insensitive LIKE for SQLAlchemy
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Lead.name.ilike(search_pattern),
                Lead.company.ilike(search_pattern)
            )
        )

    # Get all matching leads
    leads = query.all()

    # Attach computed fields to each lead
    for lead in leads:
        _attach_computed_fields(db, lead)

    return leads


def get_lead(db: Session, lead_id: str) -> Optional[Lead]:
    """
    Get a single lead by ID.

    Args:
        db: Database session
        lead_id: Lead UUID

    Returns:
        Lead object with computed fields, or None if not found
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if lead:
        _attach_computed_fields(db, lead)

    return lead


def create_lead(db: Session, data: CreateLeadRequest) -> Lead:
    """
    Create a new lead.

    Args:
        db: Database session
        data: Validated lead creation data

    Returns:
        Newly created Lead object with computed fields
    """
    # Convert Pydantic schema to ORM model
    lead = Lead(
        name=data.name,
        company=data.company,
        phone=data.phone,
        status=data.status.value  # Convert enum to string
    )

    db.add(lead)
    db.commit()
    db.refresh(lead)

    # Attach computed fields (will be empty for new lead)
    _attach_computed_fields(db, lead)

    return lead


def update_lead(
    db: Session,
    lead_id: str,
    data: UpdateLeadRequest
) -> Optional[Lead]:
    """
    Update a lead's status or follow_up_at.

    Args:
        db: Database session
        lead_id: Lead UUID
        data: Validated update data (only non-None fields are updated)

    Returns:
        Updated Lead object with computed fields, or None if not found
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if not lead:
        return None

    # Update only the fields that were provided
    if data.status is not None:
        lead.status = data.status.value

    if data.follow_up_at is not None:
        lead.follow_up_at = data.follow_up_at

    # updated_at is automatically updated by the onupdate parameter in the model
    # But we'll explicitly set it to ensure it updates even if the database doesn't
    lead.updated_at = func.now()

    db.commit()
    db.refresh(lead)

    # Attach computed fields
    _attach_computed_fields(db, lead)

    return lead


# ==================== Discussion CRUD Operations ====================

def get_discussions(db: Session, lead_id: str) -> List[Discussion]:
    """
    Get all discussions for a lead, ordered by most recent first.

    Args:
        db: Database session
        lead_id: Lead UUID

    Returns:
        List of Discussion objects in reverse chronological order
        (ordered by created_at DESC, then id DESC as tiebreaker)
    """
    discussions = (
        db.query(Discussion)
        .filter(Discussion.lead_id == lead_id)
        .order_by(desc(Discussion.created_at), desc(Discussion.id))
        .all()
    )

    return discussions


def create_discussion(
    db: Session,
    lead_id: str,
    data: CreateDiscussionRequest
) -> Optional[Discussion]:
    """
    Create a new discussion for a lead.

    IMPORTANT: If the discussion includes a follow_up_at, this function also
    updates the parent lead's follow_up_at and updated_at fields in the same
    transaction. Both operations succeed or both are rolled back.

    Args:
        db: Database session
        lead_id: Parent lead UUID
        data: Validated discussion creation data

    Returns:
        Newly created Discussion object, or None if lead not found
    """
    # Verify the lead exists
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        return None

    # Create the discussion
    discussion = Discussion(
        lead_id=lead_id,
        note=data.note,
        follow_up_at=data.follow_up_at
    )

    db.add(discussion)

    # If the discussion has a follow-up date, update the parent lead
    # This happens in the same transaction - both succeed or both fail
    if data.follow_up_at:
        lead.follow_up_at = data.follow_up_at
        lead.updated_at = func.now()

    # Single commit for both operations (atomic transaction)
    db.commit()
    db.refresh(discussion)

    return discussion


# ==================== Helper Functions ====================

def _attach_computed_fields(db: Session, lead: Lead) -> None:
    """
    Attach computed fields to a Lead object.

    These fields are NOT stored in the database but are computed from
    the discussions table and attached as dynamic attributes.

    Args:
        db: Database session
        lead: Lead object to attach fields to

    Attaches:
        - last_note: Most recent discussion note (or None)
        - last_discussion_at: Timestamp of most recent discussion (or None)
        - discussion_count: Total number of discussions
    """
    # Get the most recent discussion for this lead
    # Order by created_at DESC, then by id DESC as tiebreaker for same timestamps
    latest_discussion = (
        db.query(Discussion)
        .filter(Discussion.lead_id == lead.id)
        .order_by(desc(Discussion.created_at), desc(Discussion.id))
        .first()
    )

    # Get the total count of discussions
    discussion_count = (
        db.query(func.count(Discussion.id))
        .filter(Discussion.lead_id == lead.id)
        .scalar()
    )

    # Attach computed fields as dynamic attributes
    lead.last_note = latest_discussion.note if latest_discussion else None
    lead.last_discussion_at = latest_discussion.created_at if latest_discussion else None
    lead.discussion_count = discussion_count or 0
