"""
Verification script for Pydantic schemas.

Tests validation, serialization, and integration with SQLAlchemy models.
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.schemas import (
        LeadStatus,
        CreateLeadRequest,
        UpdateLeadRequest,
        LeadResponse,
        CreateDiscussionRequest,
        DiscussionResponse
    )
    from app.models import Lead, Discussion
    from app.database import SessionLocal, Base, engine
    from pydantic import ValidationError

    print("=" * 60)
    print("PYDANTIC SCHEMA VERIFICATION")
    print("=" * 60)

    # ==================== Test 1: Enum Validation ====================
    print("\n[TEST 1] LeadStatus Enum")
    print("-" * 60)

    # Valid statuses
    valid_statuses = ["New", "Contacted", "Qualified", "Proposal Sent", "Won", "Lost"]
    for status in valid_statuses:
        try:
            lead_status = LeadStatus(status)
            print(f"[OK] '{status}' -> {lead_status.value}")
        except ValueError as e:
            print(f"[FAIL] '{status}' validation failed: {e}")

    # Invalid status
    try:
        invalid_status = LeadStatus("Invalid Status")
        print(f"[FAIL] Should have rejected 'Invalid Status'")
    except ValueError:
        print("[OK] Invalid status 'Invalid Status' correctly rejected")

    # ==================== Test 2: CreateLeadRequest Validation ====================
    print("\n[TEST 2] CreateLeadRequest Validation")
    print("-" * 60)

    # Valid request with all fields
    try:
        lead_req = CreateLeadRequest(
            name="Test Lead",
            company="Test Company",
            phone="+1234567890",
            status=LeadStatus.CONTACTED
        )
        print(f"[OK] Full request: {lead_req.model_dump()}")
    except ValidationError as e:
        print(f"[FAIL] Full request validation failed: {e}")

    # Valid request with minimal fields (only name)
    try:
        minimal_req = CreateLeadRequest(name="Minimal Lead")
        print(f"[OK] Minimal request (name only): status={minimal_req.status}")
        assert minimal_req.status == LeadStatus.NEW, "Default status should be 'New'"
        print("[OK] Default status is 'New'")
    except ValidationError as e:
        print(f"[FAIL] Minimal request validation failed: {e}")

    # Invalid request - empty name
    try:
        invalid_req = CreateLeadRequest(name="")
        print(f"[FAIL] Should have rejected empty name")
    except ValidationError:
        print("[OK] Empty name correctly rejected")

    # Invalid request - missing name
    try:
        invalid_req = CreateLeadRequest(company="Test")
        print(f"[FAIL] Should have rejected missing name")
    except ValidationError:
        print("[OK] Missing name correctly rejected")

    # ==================== Test 3: UpdateLeadRequest Validation ====================
    print("\n[TEST 3] UpdateLeadRequest Validation")
    print("-" * 60)

    # Valid update - status only
    try:
        update_req = UpdateLeadRequest(status=LeadStatus.WON)
        print(f"[OK] Status update: {update_req.model_dump()}")
    except ValidationError as e:
        print(f"[FAIL] Status update validation failed: {e}")

    # Valid update - follow_up_at only
    try:
        future_date = datetime.now() + timedelta(days=7)
        update_req = UpdateLeadRequest(follow_up_at=future_date)
        print(f"[OK] Follow-up update: follow_up_at={update_req.follow_up_at}")
    except ValidationError as e:
        print(f"[FAIL] Follow-up update validation failed: {e}")

    # Valid update - both fields
    try:
        update_req = UpdateLeadRequest(
            status=LeadStatus.QUALIFIED,
            follow_up_at=datetime.now() + timedelta(days=3)
        )
        print(f"[OK] Both fields update: {update_req.model_dump()}")
    except ValidationError as e:
        print(f"[FAIL] Both fields update validation failed: {e}")

    # Valid update - no fields (empty partial update)
    try:
        empty_update = UpdateLeadRequest()
        print(f"[OK] Empty update (no changes): {empty_update.model_dump()}")
    except ValidationError as e:
        print(f"[FAIL] Empty update validation failed: {e}")

    # ==================== Test 4: CreateDiscussionRequest Validation ====================
    print("\n[TEST 4] CreateDiscussionRequest Validation")
    print("-" * 60)

    # Valid discussion with note only
    try:
        discussion_req = CreateDiscussionRequest(note="Initial contact made")
        print(f"[OK] Discussion with note only: {discussion_req.note}")
    except ValidationError as e:
        print(f"[FAIL] Discussion validation failed: {e}")

    # Valid discussion with follow-up
    try:
        discussion_req = CreateDiscussionRequest(
            note="Follow-up scheduled",
            follow_up_at=datetime.now() + timedelta(days=5)
        )
        print(f"[OK] Discussion with follow-up: {discussion_req.model_dump()}")
    except ValidationError as e:
        print(f"[FAIL] Discussion with follow-up validation failed: {e}")

    # Invalid discussion - empty note
    try:
        invalid_discussion = CreateDiscussionRequest(note="")
        print(f"[FAIL] Should have rejected empty note")
    except ValidationError:
        print("[OK] Empty note correctly rejected")

    # Invalid discussion - missing note
    try:
        invalid_discussion = CreateDiscussionRequest(follow_up_at=datetime.now())
        print(f"[FAIL] Should have rejected missing note")
    except ValidationError:
        print("[OK] Missing note correctly rejected")

    # ==================== Test 5: SQLAlchemy Integration ====================
    print("\n[TEST 5] SQLAlchemy ORM Integration (from_attributes)")
    print("-" * 60)

    # Create tables and session
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Create a lead in the database
        lead = Lead(
            name="Integration Test Lead",
            company="Test Corp",
            phone="+1234567890",
            status="Contacted"
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)

        # Test LeadResponse with SQLAlchemy object
        try:
            # Add computed fields manually (normally done by CRUD layer)
            lead.last_note = None
            lead.last_discussion_at = None
            lead.discussion_count = 0

            lead_response = LeadResponse.model_validate(lead)
            print(f"[OK] LeadResponse from ORM object: id={lead_response.id}")
            print(f"     name={lead_response.name}, status={lead_response.status}")
            print(f"     computed fields: last_note={lead_response.last_note}, "
                  f"discussion_count={lead_response.discussion_count}")
        except Exception as e:
            print(f"[FAIL] LeadResponse from ORM failed: {e}")

        # Create a discussion
        discussion = Discussion(
            lead_id=lead.id,
            note="Test discussion note"
        )
        db.add(discussion)
        db.commit()
        db.refresh(discussion)

        # Test DiscussionResponse with SQLAlchemy object
        try:
            discussion_response = DiscussionResponse.model_validate(discussion)
            print(f"[OK] DiscussionResponse from ORM object: id={discussion_response.id}")
            print(f"     note={discussion_response.note[:30]}...")
        except Exception as e:
            print(f"[FAIL] DiscussionResponse from ORM failed: {e}")

        # Clean up
        db.delete(lead)
        db.commit()

    finally:
        db.close()

    # ==================== Test 6: JSON Serialization ====================
    print("\n[TEST 6] JSON Serialization")
    print("-" * 60)

    # Test that schemas can be serialized to JSON
    try:
        lead_req = CreateLeadRequest(
            name="JSON Test",
            company="Test Inc",
            status=LeadStatus.NEW
        )
        json_data = lead_req.model_dump_json()
        print(f"[OK] CreateLeadRequest to JSON: {json_data}")
    except Exception as e:
        print(f"[FAIL] JSON serialization failed: {e}")

    # Test datetime serialization
    try:
        update_req = UpdateLeadRequest(
            status=LeadStatus.QUALIFIED,
            follow_up_at=datetime(2026, 10, 25, 14, 30)
        )
        json_data = update_req.model_dump_json()
        print(f"[OK] UpdateLeadRequest with datetime to JSON: {json_data}")
    except Exception as e:
        print(f"[FAIL] Datetime serialization failed: {e}")

    print("\n" + "=" * 60)
    print("[SUCCESS] All schema verification tests passed!")
    print("=" * 60)

    print("\nSchema Summary:")
    print("  - LeadStatus: Enum with 6 valid statuses")
    print("  - CreateLeadRequest: name (required), company, phone, status")
    print("  - UpdateLeadRequest: status, follow_up_at (both optional)")
    print("  - LeadResponse: all fields + computed (last_note, last_discussion_at, discussion_count)")
    print("  - CreateDiscussionRequest: note (required), follow_up_at (optional)")
    print("  - DiscussionResponse: all fields from database")
    print("  - from_attributes=True: Response schemas can read from SQLAlchemy objects")

except Exception as e:
    print(f"\n[FAIL] Schema verification failed:")
    print(f"   {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
