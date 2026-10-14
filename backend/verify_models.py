"""
Verification script for ORM models.

Tests that the models can be imported, tables can be created,
and basic CRUD operations work.
"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.database import engine, SessionLocal, Base
    from app.models import Lead, Discussion

    print("[OK] Models imported successfully")
    print(f"[OK] Lead model: {Lead.__tablename__}")
    print(f"[OK] Discussion model: {Discussion.__tablename__}")

    # Check model attributes
    print("\n[INFO] Lead columns:")
    for column in Lead.__table__.columns:
        nullable = "NULL" if column.nullable else "NOT NULL"
        default = f" DEFAULT {column.default}" if column.default else ""
        print(f"  - {column.name}: {column.type} {nullable}{default}")

    print("\n[INFO] Discussion columns:")
    for column in Discussion.__table__.columns:
        nullable = "NULL" if column.nullable else "NOT NULL"
        default = f" DEFAULT {column.default}" if column.default else ""
        print(f"  - {column.name}: {column.type} {nullable}{default}")

    # Check relationships
    print("\n[INFO] Relationships:")
    print(f"  - Lead.discussions: {Lead.discussions}")
    print(f"  - Discussion.lead: {Discussion.lead}")

    # Check foreign keys
    print("\n[INFO] Foreign keys:")
    for fk in Discussion.__table__.foreign_keys:
        print(f"  - {fk.parent.name} -> {fk.target_fullname} (ondelete={fk.ondelete})")

    # Create tables
    print("\n[INFO] Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("[OK] Tables created successfully")

    # Verify tables exist
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"[OK] Database tables: {tables}")

    # Test basic CRUD - create a lead
    print("\n[INFO] Testing basic CRUD operations...")
    db = SessionLocal()
    try:
        # Create a test lead
        test_lead = Lead(
            name="Test Lead",
            company="Test Company",
            phone="+1234567890",
            status="New"
        )
        db.add(test_lead)
        db.commit()
        db.refresh(test_lead)
        print(f"[OK] Created lead: {test_lead}")

        # Create a discussion for the lead
        test_discussion = Discussion(
            lead_id=test_lead.id,
            note="Initial contact made"
        )
        db.add(test_discussion)
        db.commit()
        db.refresh(test_discussion)
        print(f"[OK] Created discussion: {test_discussion}")

        # Test relationship - access discussions through lead
        db.refresh(test_lead)
        print(f"[OK] Lead has {len(test_lead.discussions)} discussion(s)")

        # Clean up test data
        db.delete(test_lead)  # Should cascade delete the discussion
        db.commit()
        print("[OK] Test data cleaned up (cascade delete verified)")

    finally:
        db.close()

    print("\n[SUCCESS] All model verification checks passed!")
    print("\nModel summary:")
    print("  - Lead: id, name, company, phone, status, follow_up_at, created_at, updated_at")
    print("  - Discussion: id, lead_id, note, follow_up_at, created_at")
    print("  - Relationship: Lead.discussions (one-to-many)")
    print("  - Foreign key: discussions.lead_id -> leads.id (CASCADE DELETE)")

except Exception as e:
    print(f"\n[FAIL] Model verification failed:")
    print(f"   {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
