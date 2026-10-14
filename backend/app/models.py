"""
SQLAlchemy ORM models for LeadFlow.

Defines the database schema for leads and discussions using SQLAlchemy's
declarative base. UUIDs are generated in Python and stored as TEXT for
SQLite compatibility.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Lead(Base):
    """
    Lead model representing a sales prospect.

    Attributes:
        id: UUID primary key (stored as TEXT)
        name: Lead's full name (required)
        company: Company name (optional)
        phone: Phone number (optional)
        status: Current status - one of: New, Contacted, Qualified,
                Proposal Sent, Won, Lost (required, defaults to 'New')
        follow_up_at: Next follow-up datetime (optional)
        created_at: Timestamp when lead was created
        updated_at: Timestamp when lead was last modified
        discussions: Relationship to Discussion objects (one-to-many)
    """
    __tablename__ = "leads"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    company = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    status = Column(String, nullable=False, default="New")
    follow_up_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationship: one lead has many discussions
    # back_populates allows bidirectional navigation (lead.discussions, discussion.lead)
    # cascade="all, delete-orphan" ensures discussions are deleted when lead is deleted
    discussions = relationship(
        "Discussion",
        back_populates="lead",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Lead(id={self.id}, name={self.name}, status={self.status})>"


class Discussion(Base):
    """
    Discussion model representing a conversation or note for a lead.

    Attributes:
        id: UUID primary key (stored as TEXT)
        lead_id: Foreign key to leads.id (required)
        note: Discussion content (required)
        follow_up_at: Optional follow-up datetime set during this discussion
        created_at: Timestamp when discussion was logged
        lead: Relationship to parent Lead object (many-to-one)
    """
    __tablename__ = "discussions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    lead_id = Column(String, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    note = Column(Text, nullable=False)
    follow_up_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationship: many discussions belong to one lead
    # back_populates creates bidirectional link with Lead.discussions
    lead = relationship("Lead", back_populates="discussions")

    def __repr__(self):
        return f"<Discussion(id={self.id}, lead_id={self.lead_id}, created_at={self.created_at})>"
