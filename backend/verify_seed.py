"""
Verify seed data integrity and display detailed information.
"""
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import Lead, Discussion

db = SessionLocal()

print("=" * 70)
print("SEED DATA VERIFICATION")
print("=" * 70)

# Get all leads with their discussions
leads = db.query(Lead).all()

for lead in leads:
    print(f"\n{'='*70}")
    print(f"Lead: {lead.name}")
    print(f"{'='*70}")
    print(f"Company: {lead.company or 'N/A'}")
    print(f"Phone: {lead.phone or 'N/A'}")
    print(f"Status: {lead.status}")
    print(f"Follow-up: {lead.follow_up_at.strftime('%Y-%m-%d %H:%M') if lead.follow_up_at else 'None'}")

    if lead.follow_up_at:
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        if lead.follow_up_at >= today_start and lead.follow_up_at < today_start.replace(hour=23, minute=59, second=59):
            print(f"  >> TODAY'S FOLLOW-UP")
        elif lead.follow_up_at < today_start:
            days_overdue = (now - lead.follow_up_at).days
            print(f"  >> OVERDUE ({days_overdue} days)")

    print(f"Created: {lead.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

    # Get discussions
    discussions = db.query(Discussion).filter(
        Discussion.lead_id == lead.id
    ).order_by(Discussion.created_at.desc()).all()

    print(f"\nDiscussions ({len(discussions)}):")
    if discussions:
        for i, disc in enumerate(discussions, 1):
            days_ago = (datetime.now() - disc.created_at).days
            print(f"  {i}. [{days_ago}d ago] {disc.note}")
    else:
        print("  (no discussions)")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Total leads: {len(leads)}")
print(f"Total discussions: {db.query(Discussion).count()}")

db.close()
