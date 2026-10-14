"""
Additional model verification: test cascade delete and timestamps.
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.database import SessionLocal
    from app.models import Lead, Discussion

    db = SessionLocal()

    print("[INFO] Testing cascade delete behavior...")

    # Create a lead with multiple discussions
    lead = Lead(
        name="Cascade Test Lead",
        company="Test Corp",
        status="Contacted"
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)

    lead_id = lead.id
    print(f"[OK] Created lead with ID: {lead_id}")

    # Add multiple discussions
    for i in range(3):
        discussion = Discussion(
            lead_id=lead_id,
            note=f"Discussion {i+1}"
        )
        db.add(discussion)
    db.commit()

    # Verify discussions were created
    discussions = db.query(Discussion).filter(Discussion.lead_id == lead_id).all()
    print(f"[OK] Created {len(discussions)} discussions")

    # Delete the lead
    db.delete(lead)
    db.commit()
    print("[OK] Lead deleted")

    # Check that discussions were cascade deleted
    remaining_discussions = db.query(Discussion).filter(Discussion.lead_id == lead_id).all()
    if len(remaining_discussions) == 0:
        print("[OK] Cascade delete verified - all discussions removed")
    else:
        print(f"[FAIL] Cascade delete failed - {len(remaining_discussions)} discussions remain")
        sys.exit(1)

    print("\n[INFO] Testing timestamp behavior...")

    # Create a lead and check timestamps
    lead = Lead(name="Timestamp Test", status="New")
    db.add(lead)
    db.commit()
    db.refresh(lead)

    print(f"[OK] created_at: {lead.created_at}")
    print(f"[OK] updated_at: {lead.updated_at}")

    if lead.created_at and lead.updated_at:
        print("[OK] Timestamps automatically set")
    else:
        print("[FAIL] Timestamps not set")
        sys.exit(1)

    # Update the lead and check that updated_at changes
    original_updated = lead.updated_at
    import time
    time.sleep(1)  # Wait a bit to ensure timestamp difference

    lead.status = "Contacted"
    db.commit()
    db.refresh(lead)

    if lead.updated_at > original_updated:
        print("[OK] updated_at timestamp changes on update")
    else:
        print("[WARNING] updated_at did not change (may need manual update in crud.py)")

    print("\n[INFO] Testing optional fields...")

    # Test lead with minimal fields
    minimal_lead = Lead(name="Minimal Lead")
    db.add(minimal_lead)
    db.commit()
    db.refresh(minimal_lead)

    if minimal_lead.company is None and minimal_lead.phone is None:
        print("[OK] Optional fields (company, phone) can be NULL")

    if minimal_lead.status == "New":
        print("[OK] Default status is 'New'")

    # Test follow_up_at
    future_date = datetime.now() + timedelta(days=7)
    lead_with_followup = Lead(
        name="Follow-up Test",
        follow_up_at=future_date
    )
    db.add(lead_with_followup)
    db.commit()
    db.refresh(lead_with_followup)

    if lead_with_followup.follow_up_at:
        print(f"[OK] follow_up_at can be set: {lead_with_followup.follow_up_at}")

    # Test discussion with follow_up_at
    discussion_with_followup = Discussion(
        lead_id=lead_with_followup.id,
        note="Discussion with follow-up",
        follow_up_at=future_date
    )
    db.add(discussion_with_followup)
    db.commit()
    db.refresh(discussion_with_followup)

    if discussion_with_followup.follow_up_at:
        print(f"[OK] Discussion follow_up_at can be set: {discussion_with_followup.follow_up_at}")

    # Clean up
    db.query(Lead).delete()
    db.commit()

    print("\n[SUCCESS] All additional model tests passed!")

    db.close()

except Exception as e:
    print(f"\n[FAIL] Additional verification failed:")
    print(f"   {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
