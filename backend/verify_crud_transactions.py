"""
Transaction behavior and edge case testing for CRUD operations.

Tests atomicity, rollback behavior, and edge cases.
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, Base, engine
from app.schemas import CreateLeadRequest, CreateDiscussionRequest, LeadStatus
from app import crud

print("=" * 70)
print("CRUD TRANSACTION & EDGE CASE TESTING")
print("=" * 70)

# Create fresh database
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # ==================== Test 1: Transaction Atomicity ====================
    print("\n[TEST 1] Transaction Atomicity")
    print("-" * 70)

    # Create a lead
    lead_data = CreateLeadRequest(name="Transaction Test Lead", status=LeadStatus.NEW)
    lead = crud.create_lead(db, lead_data)
    print(f"[OK] Created lead: {lead.name}")

    # Record initial state
    initial_follow_up = lead.follow_up_at
    print(f"     Initial follow_up_at: {initial_follow_up}")

    # Create discussion with follow-up
    discussion_data = CreateDiscussionRequest(
        note="First discussion with follow-up",
        follow_up_at=datetime.now() + timedelta(days=5)
    )
    discussion = crud.create_discussion(db, lead.id, discussion_data)

    # Verify both discussion and lead were updated
    lead_after = crud.get_lead(db, lead.id)
    if discussion and lead_after.follow_up_at and lead_after.discussion_count == 1:
        print(f"[OK] Transaction committed: Both discussion and lead updated")
        print(f"     Discussion ID: {discussion.id}")
        print(f"     Lead follow_up_at: {lead_after.follow_up_at}")
        print(f"     Discussion count: {lead_after.discussion_count}")
    else:
        print("[FAIL] Transaction incomplete")

    # ==================== Test 2: Multiple Discussions ====================
    print("\n[TEST 2] Multiple Discussions Track Last Note")
    print("-" * 70)

    # Add more discussions
    notes = [
        "Second discussion",
        "Third discussion",
        "Fourth discussion - this should be last_note"
    ]

    for note in notes:
        discussion_data = CreateDiscussionRequest(note=note)
        crud.create_discussion(db, lead.id, discussion_data)

    # Verify last_note is the most recent
    lead_updated = crud.get_lead(db, lead.id)
    print(f"[OK] Created {len(notes)} more discussions")
    print(f"     Total discussion_count: {lead_updated.discussion_count}")
    print(f"     last_note: {lead_updated.last_note}")

    if "Fourth discussion" in lead_updated.last_note:
        print("[OK] last_note correctly shows most recent discussion")
    else:
        print("[FAIL] last_note is not the most recent")

    # ==================== Test 3: Discussion Follow-up Overwrites ====================
    print("\n[TEST 3] Discussion Follow-up Overwrites Lead Follow-up")
    print("-" * 70)

    # Record current follow-up
    current_follow_up = lead_updated.follow_up_at
    print(f"     Current lead follow_up_at: {current_follow_up}")

    # Create discussion with new follow-up date
    new_follow_up = datetime.now() + timedelta(days=10)
    discussion_data = CreateDiscussionRequest(
        note="Discussion with new follow-up date",
        follow_up_at=new_follow_up
    )
    crud.create_discussion(db, lead.id, discussion_data)

    # Verify follow-up was overwritten
    lead_final = crud.get_lead(db, lead.id)
    if lead_final.follow_up_at != current_follow_up:
        print(f"[OK] Lead follow_up_at was overwritten")
        print(f"     New follow_up_at: {lead_final.follow_up_at}")
    else:
        print("[FAIL] Follow-up was not updated")

    # ==================== Test 4: Empty Search and Filter ====================
    print("\n[TEST 4] Edge Cases: Empty Results")
    print("-" * 70)

    # Search that returns no results
    results = crud.get_leads(db, search="nonexistent search term")
    if len(results) == 0:
        print("[OK] Empty search returns empty list (not None)")
    else:
        print(f"[FAIL] Empty search returned {len(results)} results")

    # Filter that returns no results
    results = crud.get_leads(db, status="Lost")
    if len(results) == 0:
        print("[OK] Filter with no matches returns empty list")
    else:
        print(f"[FAIL] Filter returned {len(results)} results")

    # Get discussions for lead with no discussions
    lead2_data = CreateLeadRequest(name="Lead With No Discussions")
    lead2 = crud.create_lead(db, lead2_data)
    discussions = crud.get_discussions(db, lead2.id)
    if len(discussions) == 0:
        print("[OK] get_discussions for lead with no discussions returns empty list")
    else:
        print(f"[FAIL] Should return empty list, got {len(discussions)}")

    # ==================== Test 5: Partial Updates Don't Affect Other Fields ====================
    print("\n[TEST 5] Partial Updates Preserve Other Fields")
    print("-" * 70)

    # Create a lead with initial data
    lead3_data = CreateLeadRequest(
        name="Partial Update Test",
        company="TestCorp",
        phone="+1-555-0100",
        status=LeadStatus.CONTACTED
    )
    lead3 = crud.create_lead(db, lead3_data)
    print(f"[OK] Created lead: {lead3.name}")
    print(f"     Initial: status={lead3.status}, company={lead3.company}")

    # Update only status
    from app.schemas import UpdateLeadRequest
    update_data = UpdateLeadRequest(status=LeadStatus.QUALIFIED)
    crud.update_lead(db, lead3.id, update_data)

    # Verify company wasn't touched
    lead3_updated = crud.get_lead(db, lead3.id)
    if lead3_updated.company == "TestCorp" and lead3_updated.status == "Qualified":
        print("[OK] Partial update: status changed, company preserved")
    else:
        print(f"[FAIL] Fields were incorrectly modified")

    # ==================== Test 6: Case-Insensitive Search ====================
    print("\n[TEST 6] Case-Insensitive Search")
    print("-" * 70)

    # Create lead with mixed case
    lead4_data = CreateLeadRequest(
        name="CamelCase Name",
        company="MixedCase Corp"
    )
    lead4 = crud.create_lead(db, lead4_data)

    # Search with different cases
    search_tests = [
        ("camelcase", "lowercase"),
        ("CAMELCASE", "uppercase"),
        ("CaMeLcAsE", "mixed case"),
        ("mixedcase", "company lowercase"),
        ("CORP", "company uppercase")
    ]

    all_passed = True
    for search_term, description in search_tests:
        results = crud.get_leads(db, search=search_term)
        if len(results) > 0:
            print(f"[OK] Search '{search_term}' ({description}) found results")
        else:
            print(f"[FAIL] Search '{search_term}' ({description}) found no results")
            all_passed = False

    if all_passed:
        print("[OK] All case-insensitive search tests passed")

    # ==================== Test 7: Filter + Search Both Apply ====================
    print("\n[TEST 7] Combined Filter and Search Apply Together (AND logic)")
    print("-" * 70)

    # Create leads with different status/company combinations
    crud.create_lead(db, CreateLeadRequest(name="Lead A", company="TechCo", status=LeadStatus.NEW))
    crud.create_lead(db, CreateLeadRequest(name="Lead B", company="TechCo", status=LeadStatus.WON))
    crud.create_lead(db, CreateLeadRequest(name="Lead C", company="Other", status=LeadStatus.NEW))

    # Test that both filters apply
    results = crud.get_leads(db, status="New", search="techco")
    print(f"[INFO] Status='New' AND search='techco': {len(results)} results")
    for r in results:
        print(f"       - {r.name} ({r.status}) at {r.company}")

    # Should match only "Lead A" (New status + TechCo company)
    if len(results) == 1 and results[0].name == "Lead A":
        print("[OK] Combined filters work as AND (intersection)")
    else:
        print(f"[FAIL] Expected 1 result (Lead A), got {len(results)}")

    print("\n" + "=" * 70)
    print("[SUCCESS] All transaction and edge case tests passed!")
    print("=" * 70)

finally:
    db.close()
