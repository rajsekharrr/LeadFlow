"""
Database seed script for LeadFlow.

Populates the database with realistic sample data for development and demo purposes.
Clears existing data before seeding to ensure clean, repeatable state.

Run from backend directory:
    python seed.py
"""
import sys
import os
from datetime import datetime, timedelta

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.models import Lead, Discussion

# Seed data with Indian fintech companies (appropriate for PravarAI's domain)
LEADS = [
    {
        "name": "Ananya Krishnan",
        "company": "Zerodha Capital",
        "phone": "+91 98100 11223",
        "status": "Qualified",
        "follow_up_at": "today",  # Today at 14:00
        "discussions": [
            {"note": "Initial call — interested in SIP automation advisory.", "days_ago": 10},
            {"note": "Sent product deck. She reviewed and had good questions about AUM thresholds.", "days_ago": 5},
            {"note": "Follow-up call went well. Requested a demo.", "days_ago": 1},
        ]
    },
    {
        "name": "Rohan Mehta",
        "company": "Angel One",
        "phone": "+91 99100 44556",
        "status": "Proposal Sent",
        "follow_up_at": "overdue",  # 3 days ago (overdue)
        "discussions": [
            {"note": "Connected via LinkedIn. Warm intro from existing client.", "days_ago": 20},
            {"note": "Discovery call done. Pain point: manual client reporting.", "days_ago": 14},
            {"note": "Proposal PDF sent over email. Awaiting response.", "days_ago": 4},
        ]
    },
    {
        "name": "Priya Desai",
        "company": "Motilal Oswal",
        "phone": None,
        "status": "Contacted",
        "follow_up_at": None,
        "discussions": [
            {"note": "Cold email opened. Replied asking for a brochure.", "days_ago": 7},
            {"note": "Sent brochure. No response yet.", "days_ago": 3},
        ]
    },
    {
        "name": "Karan Bhatia",
        "company": "HDFC Securities",
        "phone": "+91 87900 66778",
        "status": "Won",
        "follow_up_at": None,
        "discussions": [
            {"note": "Signed onboarding agreement. First payment received.", "days_ago": 2},
            {"note": "Kickoff call scheduled for next week.", "days_ago": 1},
        ]
    },
    {
        "name": "Sneha Iyer",
        "company": None,
        "phone": "+91 95500 99001",
        "status": "New",
        "follow_up_at": None,
        "discussions": []
    },
]


def clear_database(db):
    """
    Clear all existing data from the database.

    Deletes in correct order to respect foreign key constraints.
    """
    print("Clearing existing data...")

    # Delete discussions first (has foreign key to leads)
    deleted_discussions = db.query(Discussion).delete()
    print(f"  Deleted {deleted_discussions} discussion(s)")

    # Delete leads
    deleted_leads = db.query(Lead).delete()
    print(f"  Deleted {deleted_leads} lead(s)")

    db.commit()
    print("Database cleared successfully\n")


def seed_database(db):
    """
    Populate database with sample data.
    """
    print("Seeding database...")
    now = datetime.now()

    for lead_data in LEADS:
        # Create lead
        lead = Lead(
            name=lead_data["name"],
            company=lead_data["company"],
            phone=lead_data["phone"],
            status=lead_data["status"]
        )

        # Set follow_up_at based on specification
        if lead_data["follow_up_at"] == "today":
            # Today at 14:00 (2 PM)
            lead.follow_up_at = now.replace(hour=14, minute=0, second=0, microsecond=0)
        elif lead_data["follow_up_at"] == "overdue":
            # 3 days ago at 10:00 AM (overdue)
            lead.follow_up_at = (now - timedelta(days=3)).replace(hour=10, minute=0, second=0, microsecond=0)
        else:
            lead.follow_up_at = None

        db.add(lead)
        db.flush()  # Get lead.id without committing

        print(f"  Created lead: {lead.name} ({lead.status})")
        if lead.follow_up_at:
            status = "TODAY" if lead_data["follow_up_at"] == "today" else "OVERDUE"
            print(f"    Follow-up: {lead.follow_up_at.strftime('%Y-%m-%d %H:%M')} [{status}]")

        # Create discussions
        for disc_data in lead_data["discussions"]:
            discussion = Discussion(
                lead_id=lead.id,
                note=disc_data["note"],
                # Backdate created_at to show realistic "time ago"
                created_at=now - timedelta(days=disc_data["days_ago"])
            )
            db.add(discussion)

        if lead_data["discussions"]:
            print(f"    Added {len(lead_data['discussions'])} discussion(s)")

    db.commit()
    print(f"\nSeeded {len(LEADS)} leads successfully!")


def verify_seed_data(db):
    """
    Verify that seed data was created correctly.
    """
    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)

    # Count leads
    lead_count = db.query(Lead).count()
    print(f"\nTotal leads: {lead_count}")

    # Count discussions
    discussion_count = db.query(Discussion).count()
    print(f"Total discussions: {discussion_count}")

    # Check follow-ups
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Today's follow-ups
    today_followups = db.query(Lead).filter(
        Lead.follow_up_at >= today_start,
        Lead.follow_up_at <= today_end
    ).all()

    print(f"\nFollow-ups scheduled for today: {len(today_followups)}")
    for lead in today_followups:
        print(f"  - {lead.name} at {lead.follow_up_at.strftime('%H:%M')}")

    # Overdue follow-ups
    overdue_followups = db.query(Lead).filter(
        Lead.follow_up_at < today_start,
        Lead.follow_up_at.isnot(None)
    ).all()

    print(f"\nOverdue follow-ups: {len(overdue_followups)}")
    for lead in overdue_followups:
        days_overdue = (now - lead.follow_up_at).days
        print(f"  - {lead.name} ({days_overdue} days overdue)")

    # Status breakdown
    print("\nLeads by status:")
    statuses = ["New", "Contacted", "Qualified", "Proposal Sent", "Won", "Lost"]
    for status in statuses:
        count = db.query(Lead).filter(Lead.status == status).count()
        if count > 0:
            print(f"  - {status}: {count}")

    # Lead with no discussions
    no_discussions = db.query(Lead).outerjoin(Discussion).filter(
        Discussion.id.is_(None)
    ).all()

    print(f"\nLeads with no discussions: {len(no_discussions)}")
    for lead in no_discussions:
        print(f"  - {lead.name}")


def main():
    """
    Main seed script execution.
    """
    print("=" * 70)
    print("LEADFLOW DATABASE SEED SCRIPT")
    print("=" * 70)
    print()

    db = SessionLocal()

    try:
        # Clear existing data
        clear_database(db)

        # Seed new data
        seed_database(db)

        # Verify results
        verify_seed_data(db)

        print("\n" + "=" * 70)
        print("SEED COMPLETE")
        print("=" * 70)
        print("\nYou can now:")
        print("  1. Start the backend: uvicorn app.main:app --reload --port 8000")
        print("  2. Visit the API: http://localhost:8000/docs")
        print("  3. Test with the frontend once it's built")

    except Exception as e:
        print(f"\n[ERROR] Seed script failed: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    main()
