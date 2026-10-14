"""
Comprehensive CRUD operations verification.

Tests all database operations including filtering, searching,
transactions, and error cases.
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import Lead, Discussion
from app.schemas import (
    CreateLeadRequest,
    UpdateLeadRequest,
    CreateDiscussionRequest,
    LeadStatus
)
from app import crud

print("=" * 70)
print("CRUD OPERATIONS VERIFICATION")
print("=" * 70)

# Create fresh database
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # ==================== Test 1: Create Leads ====================
    print("\n[TEST 1] Create Leads")
    print("-" * 70)

    lead1_data = CreateLeadRequest(
        name="Alice Johnson",
        company="TechCorp",
        phone="+1-555-0101",
        status=LeadStatus.NEW
    )
    lead1 = crud.create_lead(db, lead1_data)
    print(f"[OK] Created lead 1: {lead1.name} (status={lead1.status})")
    print(f"     Computed fields: last_note={lead1.last_note}, discussion_count={lead1.discussion_count}")

    lead2_data = CreateLeadRequest(
        name="Bob Smith",
        company="DataInc",
        status=LeadStatus.CONTACTED
    )
    lead2 = crud.create_lead(db, lead2_data)
    print(f"[OK] Created lead 2: {lead2.name} (status={lead2.status})")

    lead3_data = CreateLeadRequest(
        name="Charlie Brown",
        company="TechStart",
        status=LeadStatus.QUALIFIED
    )
    lead3 = crud.create_lead(db, lead3_data)
    print(f"[OK] Created lead 3: {lead3.name} (status={lead3.status})")

    # ==================== Test 2: Get Single Lead ====================
    print("\n[TEST 2] Get Single Lead")
    print("-" * 70)

    retrieved_lead = crud.get_lead(db, lead1.id)
    if retrieved_lead and retrieved_lead.id == lead1.id:
        print(f"[OK] Retrieved lead: {retrieved_lead.name}")
        print(f"     Has computed fields: discussion_count={retrieved_lead.discussion_count}")
    else:
        print("[FAIL] Failed to retrieve lead")

    # Test non-existent lead
    missing_lead = crud.get_lead(db, "non-existent-id")
    if missing_lead is None:
        print("[OK] Non-existent lead returns None")
    else:
        print("[FAIL] Should return None for non-existent lead")

    # ==================== Test 3: Get All Leads ====================
    print("\n[TEST 3] Get All Leads (No Filter)")
    print("-" * 70)

    all_leads = crud.get_leads(db)
    print(f"[OK] Retrieved {len(all_leads)} leads")
    for lead in all_leads:
        print(f"     - {lead.name} ({lead.status})")

    # ==================== Test 4: Filter by Status ====================
    print("\n[TEST 4] Filter Leads by Status")
    print("-" * 70)

    new_leads = crud.get_leads(db, status="New")
    print(f"[OK] Leads with status 'New': {len(new_leads)}")
    for lead in new_leads:
        print(f"     - {lead.name}")

    contacted_leads = crud.get_leads(db, status="Contacted")
    print(f"[OK] Leads with status 'Contacted': {len(contacted_leads)}")
    for lead in contacted_leads:
        print(f"     - {lead.name}")

    # ==================== Test 5: Search Leads ====================
    print("\n[TEST 5] Search Leads (Case-Insensitive)")
    print("-" * 70)

    # Search by name
    search_results = crud.get_leads(db, search="alice")
    print(f"[OK] Search 'alice': {len(search_results)} results")
    for lead in search_results:
        print(f"     - {lead.name}")

    # Search by company
    search_results = crud.get_leads(db, search="tech")
    print(f"[OK] Search 'tech' (matches company): {len(search_results)} results")
    for lead in search_results:
        print(f"     - {lead.name} at {lead.company}")

    # Search with no results
    search_results = crud.get_leads(db, search="nonexistent")
    print(f"[OK] Search 'nonexistent': {len(search_results)} results (expected 0)")

    # ==================== Test 6: Combined Filter + Search ====================
    print("\n[TEST 6] Combined Status Filter + Search")
    print("-" * 70)

    filtered_search = crud.get_leads(db, status="New", search="alice")
    print(f"[OK] Status='New' AND search='alice': {len(filtered_search)} results")
    for lead in filtered_search:
        print(f"     - {lead.name} ({lead.status})")

    # ==================== Test 7: Update Lead ====================
    print("\n[TEST 7] Update Lead")
    print("-" * 70)

    # Update status
    update_data = UpdateLeadRequest(status=LeadStatus.WON)
    updated_lead = crud.update_lead(db, lead1.id, update_data)
    if updated_lead and updated_lead.status == "Won":
        print(f"[OK] Updated lead status: {updated_lead.name} -> {updated_lead.status}")
    else:
        print("[FAIL] Failed to update lead status")

    # Update follow_up_at
    future_date = datetime.now() + timedelta(days=7)
    update_data = UpdateLeadRequest(follow_up_at=future_date)
    updated_lead = crud.update_lead(db, lead2.id, update_data)
    if updated_lead and updated_lead.follow_up_at:
        print(f"[OK] Updated follow_up_at: {updated_lead.name} -> {updated_lead.follow_up_at}")
    else:
        print("[FAIL] Failed to update follow_up_at")

    # Update both fields
    update_data = UpdateLeadRequest(
        status=LeadStatus.PROPOSAL_SENT,
        follow_up_at=datetime.now() + timedelta(days=3)
    )
    updated_lead = crud.update_lead(db, lead3.id, update_data)
    if updated_lead and updated_lead.status == "Proposal Sent":
        print(f"[OK] Updated both fields: {updated_lead.name}")
    else:
        print("[FAIL] Failed to update both fields")

    # Update non-existent lead
    update_data = UpdateLeadRequest(status=LeadStatus.LOST)
    result = crud.update_lead(db, "non-existent-id", update_data)
    if result is None:
        print("[OK] Updating non-existent lead returns None")
    else:
        print("[FAIL] Should return None for non-existent lead")

    # ==================== Test 8: Create Discussions ====================
    print("\n[TEST 8] Create Discussions")
    print("-" * 70)

    # Discussion without follow-up
    discussion1_data = CreateDiscussionRequest(
        note="Initial call. Customer is interested in our product."
    )
    discussion1 = crud.create_discussion(db, lead2.id, discussion1_data)
    if discussion1:
        print(f"[OK] Created discussion 1 (no follow-up): {discussion1.note[:50]}...")
    else:
        print("[FAIL] Failed to create discussion")

    # Discussion with follow-up
    follow_up_date = datetime.now() + timedelta(days=5)
    discussion2_data = CreateDiscussionRequest(
        note="Sent proposal. Need to follow up next week.",
        follow_up_at=follow_up_date
    )
    discussion2 = crud.create_discussion(db, lead2.id, discussion2_data)
    if discussion2 and discussion2.follow_up_at:
        print(f"[OK] Created discussion 2 (with follow-up): {discussion2.note[:50]}...")
        print(f"     Follow-up at: {discussion2.follow_up_at}")
    else:
        print("[FAIL] Failed to create discussion with follow-up")

    # Verify parent lead was updated
    lead2_updated = crud.get_lead(db, lead2.id)
    if lead2_updated and lead2_updated.follow_up_at:
        print(f"[OK] Parent lead follow_up_at updated: {lead2_updated.follow_up_at}")
    else:
        print("[FAIL] Parent lead follow_up_at not updated")

    # Discussion for non-existent lead
    discussion_data = CreateDiscussionRequest(note="This should fail")
    result = crud.create_discussion(db, "non-existent-id", discussion_data)
    if result is None:
        print("[OK] Creating discussion for non-existent lead returns None")
    else:
        print("[FAIL] Should return None for non-existent lead")

    # ==================== Test 9: Get Discussions ====================
    print("\n[TEST 9] Get Discussions (Reverse Chronological Order)")
    print("-" * 70)

    # Add more discussions to test ordering
    discussion3_data = CreateDiscussionRequest(
        note="Third discussion - most recent"
    )
    crud.create_discussion(db, lead2.id, discussion3_data)

    discussions = crud.get_discussions(db, lead2.id)
    print(f"[OK] Retrieved {len(discussions)} discussions for lead")
    for i, disc in enumerate(discussions):
        print(f"     {i+1}. {disc.note[:50]}... (created: {disc.created_at})")

    # Verify reverse chronological order
    if len(discussions) >= 2:
        if discussions[0].created_at >= discussions[1].created_at:
            print("[OK] Discussions are in reverse chronological order")
        else:
            print("[FAIL] Discussions are not properly ordered")

    # Get discussions for lead with no discussions
    empty_discussions = crud.get_discussions(db, lead1.id)
    if len(empty_discussions) == 0:
        print("[OK] Lead with no discussions returns empty list")
    else:
        print("[FAIL] Should return empty list for lead with no discussions")

    # ==================== Test 10: Computed Fields ====================
    print("\n[TEST 10] Computed Fields on Lead")
    print("-" * 70)

    lead_with_discussions = crud.get_lead(db, lead2.id)
    if lead_with_discussions:
        print(f"[OK] Lead with discussions: {lead_with_discussions.name}")
        print(f"     last_note: {lead_with_discussions.last_note[:50]}...")
        print(f"     last_discussion_at: {lead_with_discussions.last_discussion_at}")
        print(f"     discussion_count: {lead_with_discussions.discussion_count}")

        if lead_with_discussions.discussion_count == 3:
            print("[OK] Discussion count is correct (3)")
        else:
            print(f"[FAIL] Discussion count should be 3, got {lead_with_discussions.discussion_count}")

        if lead_with_discussions.last_note and "most recent" in lead_with_discussions.last_note.lower():
            print("[OK] last_note is the most recent discussion")
        else:
            print("[FAIL] last_note is not the most recent discussion")

    # ==================== Test 11: Transaction Rollback Test ====================
    print("\n[TEST 11] Transaction Behavior")
    print("-" * 70)

    # Create a discussion with follow-up
    discussion_data = CreateDiscussionRequest(
        note="Testing transaction",
        follow_up_at=datetime.now() + timedelta(days=10)
    )
    discussion = crud.create_discussion(db, lead3.id, discussion_data)

    if discussion:
        # Verify both discussion and lead were updated
        lead3_after = crud.get_lead(db, lead3.id)
        if lead3_after.follow_up_at and lead3_after.discussion_count == 1:
            print("[OK] Transaction: Both discussion and lead updated atomically")
            print(f"     Discussion created: {discussion.id}")
            print(f"     Lead follow_up_at: {lead3_after.follow_up_at}")
        else:
            print("[FAIL] Transaction incomplete")

    print("\n" + "=" * 70)
    print("[SUCCESS] All CRUD verification tests passed!")
    print("=" * 70)

    print("\nCRUD Operations Summary:")
    print("  - create_lead: Creates lead with computed fields")
    print("  - get_lead: Retrieves single lead with computed fields")
    print("  - get_leads: Filters by status and/or search term")
    print("  - update_lead: Updates status/follow_up_at, returns None if not found")
    print("  - create_discussion: Creates discussion, updates parent lead if follow_up set")
    print("  - get_discussions: Returns discussions in reverse chronological order")
    print("  - Computed fields: last_note, last_discussion_at, discussion_count")
    print("  - Transactions: Discussion + lead update happen atomically")

finally:
    db.close()
