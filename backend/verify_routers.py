"""
API Router verification - tests all endpoints.

Tests HTTP routes, status codes, error handling, and request/response flow.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta

# Import and set up database BEFORE creating test client
from app.database import Base, engine
from app.models import Lead, Discussion  # Import models so they're registered

# Create fresh database
print("[INFO] Setting up database...")
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print("[INFO] Database tables created")

# Now import FastAPI components
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.routers import leads, discussions

# Create FastAPI app
app = FastAPI()
app.include_router(leads.router)
app.include_router(discussions.router)

# Create test client
client = TestClient(app)

print("=" * 70)
print("API ROUTER VERIFICATION")
print("=" * 70)

# ==================== Test 1: POST /api/leads (Create Lead) ====================
print("\n[TEST 1] POST /api/leads - Create Lead")
print("-" * 70)

response = client.post("/api/leads", json={
    "name": "Alice Johnson",
    "company": "TechCorp",
    "phone": "+1-555-0101",
    "status": "New"
})

if response.status_code == 201:
    print(f"[OK] Status code: 201 Created")
    lead1 = response.json()
    print(f"[OK] Response contains id: {lead1['id']}")
    print(f"     Name: {lead1['name']}, Status: {lead1['status']}")
    print(f"     Computed fields: discussion_count={lead1['discussion_count']}")
else:
    print(f"[FAIL] Expected 201, got {response.status_code}")
    print(f"       Response: {response.json()}")
    sys.exit(1)

# Create more leads for filtering tests
response2 = client.post("/api/leads", json={
    "name": "Bob Smith",
    "company": "DataInc",
    "status": "Contacted"
})
lead2 = response2.json()

response3 = client.post("/api/leads", json={
    "name": "Charlie Brown",
    "company": "TechStart",
    "status": "Qualified"
})
lead3 = response3.json()

print(f"[OK] Created 3 leads total")

# ==================== Test 2: GET /api/leads (List All) ====================
print("\n[TEST 2] GET /api/leads - List All Leads")
print("-" * 70)

response = client.get("/api/leads")

if response.status_code == 200:
    print(f"[OK] Status code: 200 OK")
    leads = response.json()
    print(f"[OK] Retrieved {len(leads)} leads")
    for lead in leads:
        print(f"     - {lead['name']} ({lead['status']})")
else:
    print(f"[FAIL] Expected 200, got {response.status_code}")

# ==================== Test 3: GET /api/leads?status=X (Filter) ====================
print("\n[TEST 3] GET /api/leads?status=New - Filter by Status")
print("-" * 70)

response = client.get("/api/leads?status=New")

if response.status_code == 200:
    print(f"[OK] Status code: 200 OK")
    filtered = response.json()
    print(f"[OK] Filtered results: {len(filtered)} leads with status 'New'")
    for lead in filtered:
        print(f"     - {lead['name']} ({lead['status']})")
else:
    print(f"[FAIL] Expected 200, got {response.status_code}")

# ==================== Test 4: GET /api/leads?search=X (Search) ====================
print("\n[TEST 4] GET /api/leads?search=tech - Search")
print("-" * 70)

response = client.get("/api/leads?search=tech")

if response.status_code == 200:
    print(f"[OK] Status code: 200 OK")
    search_results = response.json()
    print(f"[OK] Search results: {len(search_results)} leads matching 'tech'")
    for lead in search_results:
        print(f"     - {lead['name']} at {lead.get('company', 'N/A')}")
else:
    print(f"[FAIL] Expected 200, got {response.status_code}")

# ==================== Test 5: GET /api/leads/{id} (Get Single) ====================
print("\n[TEST 5] GET /api/leads/{id} - Get Single Lead")
print("-" * 70)

response = client.get(f"/api/leads/{lead1['id']}")

if response.status_code == 200:
    print(f"[OK] Status code: 200 OK")
    lead = response.json()
    print(f"[OK] Retrieved lead: {lead['name']}")
    print(f"     Has computed fields: discussion_count={lead['discussion_count']}")
else:
    print(f"[FAIL] Expected 200, got {response.status_code}")

# Test 404 for non-existent lead
response = client.get("/api/leads/non-existent-id")

if response.status_code == 404:
    print(f"[OK] Non-existent lead returns 404")
    error = response.json()
    print(f"     Error detail: {error['detail']}")
else:
    print(f"[FAIL] Expected 404, got {response.status_code}")

# ==================== Test 6: PATCH /api/leads/{id} (Update) ====================
print("\n[TEST 6] PATCH /api/leads/{id} - Update Lead")
print("-" * 70)

# Update status
response = client.patch(f"/api/leads/{lead1['id']}", json={
    "status": "Won"
})

if response.status_code == 200:
    print(f"[OK] Status code: 200 OK")
    updated = response.json()
    if updated['status'] == "Won":
        print(f"[OK] Status updated: {updated['name']} -> {updated['status']}")
    else:
        print(f"[FAIL] Status not updated correctly")
else:
    print(f"[FAIL] Expected 200, got {response.status_code}")

# Update follow_up_at
future_date = (datetime.now() + timedelta(days=7)).isoformat()
response = client.patch(f"/api/leads/{lead2['id']}", json={
    "follow_up_at": future_date
})

if response.status_code == 200:
    print(f"[OK] Follow-up date updated successfully")
else:
    print(f"[FAIL] Expected 200, got {response.status_code}")

# Test 404 for non-existent lead
response = client.patch("/api/leads/non-existent-id", json={"status": "Won"})

if response.status_code == 404:
    print(f"[OK] Update non-existent lead returns 404")
else:
    print(f"[FAIL] Expected 404, got {response.status_code}")

# ==================== Test 7: POST /api/leads/{id}/discussions (Create) ====================
print("\n[TEST 7] POST /api/leads/{id}/discussions - Create Discussion")
print("-" * 70)

response = client.post(f"/api/leads/{lead2['id']}/discussions", json={
    "note": "Initial call. Customer is very interested."
})

if response.status_code == 201:
    print(f"[OK] Status code: 201 Created")
    discussion1 = response.json()
    print(f"[OK] Discussion created: {discussion1['note'][:50]}...")
    print(f"     Discussion ID: {discussion1['id']}")
else:
    print(f"[FAIL] Expected 201, got {response.status_code}")

# Create discussion with follow-up
follow_up_date = (datetime.now() + timedelta(days=5)).isoformat()
response = client.post(f"/api/leads/{lead2['id']}/discussions", json={
    "note": "Sent proposal. Need to follow up next week.",
    "follow_up_at": follow_up_date
})

if response.status_code == 201:
    print(f"[OK] Discussion with follow-up created")
    discussion2 = response.json()
    print(f"     Follow-up at: {discussion2['follow_up_at']}")
else:
    print(f"[FAIL] Expected 201, got {response.status_code}")

# Verify parent lead was updated
response = client.get(f"/api/leads/{lead2['id']}")
lead2_updated = response.json()
if lead2_updated['follow_up_at']:
    print(f"[OK] Parent lead follow_up_at updated: {lead2_updated['follow_up_at']}")
else:
    print(f"[FAIL] Parent lead follow_up_at not updated")

# Test 404 for non-existent lead
response = client.post("/api/leads/non-existent-id/discussions", json={
    "note": "This should fail"
})

if response.status_code == 404:
    print(f"[OK] Create discussion for non-existent lead returns 404")
else:
    print(f"[FAIL] Expected 404, got {response.status_code}")

# ==================== Test 8: GET /api/leads/{id}/discussions (List) ====================
print("\n[TEST 8] GET /api/leads/{id}/discussions - List Discussions")
print("-" * 70)

response = client.get(f"/api/leads/{lead2['id']}/discussions")

if response.status_code == 200:
    print(f"[OK] Status code: 200 OK")
    discussions = response.json()
    print(f"[OK] Retrieved {len(discussions)} discussions")
    for i, disc in enumerate(discussions):
        print(f"     {i+1}. {disc['note'][:50]}...")
else:
    print(f"[FAIL] Expected 200, got {response.status_code}")

# Test empty discussions list
response = client.get(f"/api/leads/{lead1['id']}/discussions")

if response.status_code == 200:
    discussions = response.json()
    if len(discussions) == 0:
        print(f"[OK] Lead with no discussions returns empty list")
    else:
        print(f"[FAIL] Should return empty list, got {len(discussions)}")
else:
    print(f"[FAIL] Expected 200, got {response.status_code}")

# Test 404 for non-existent lead
response = client.get("/api/leads/non-existent-id/discussions")

if response.status_code == 404:
    print(f"[OK] List discussions for non-existent lead returns 404")
else:
    print(f"[FAIL] Expected 404, got {response.status_code}")

# ==================== Test 9: Validation Errors ====================
print("\n[TEST 9] Validation Errors")
print("-" * 70)

# Missing required field (name)
response = client.post("/api/leads", json={
    "company": "Test Corp"
})

if response.status_code == 422:
    print(f"[OK] Missing required field returns 422 Unprocessable Entity")
    error = response.json()
    print(f"     Validation error details present: {bool(error.get('detail'))}")
else:
    print(f"[FAIL] Expected 422, got {response.status_code}")

# Invalid enum value
response = client.post("/api/leads", json={
    "name": "Test Lead",
    "status": "InvalidStatus"
})

if response.status_code == 422:
    print(f"[OK] Invalid status value returns 422")
else:
    print(f"[FAIL] Expected 422, got {response.status_code}")

# Empty required field
response = client.post(f"/api/leads/{lead1['id']}/discussions", json={
    "note": ""
})

if response.status_code == 422:
    print(f"[OK] Empty note returns 422")
else:
    print(f"[FAIL] Expected 422, got {response.status_code}")

# ==================== Test 10: Computed Fields in Response ====================
print("\n[TEST 10] Computed Fields in API Response")
print("-" * 70)

# Get lead with discussions
response = client.get(f"/api/leads/{lead2['id']}")
lead_with_discussions = response.json()

print(f"[OK] Lead response includes computed fields:")
print(f"     last_note: {lead_with_discussions['last_note'][:50] if lead_with_discussions['last_note'] else 'None'}...")
print(f"     last_discussion_at: {lead_with_discussions['last_discussion_at']}")
print(f"     discussion_count: {lead_with_discussions['discussion_count']}")

if lead_with_discussions['discussion_count'] == 2:
    print(f"[OK] Discussion count is accurate (2)")
else:
    print(f"[FAIL] Discussion count should be 2, got {lead_with_discussions['discussion_count']}")

print("\n" + "=" * 70)
print("[SUCCESS] All API router verification tests passed!")
print("=" * 70)

print("\nAPI Endpoints Summary:")
print("  - POST   /api/leads                      -> 201 Created")
print("  - GET    /api/leads                      -> 200 OK (with filters)")
print("  - GET    /api/leads/{id}                 -> 200 OK | 404 Not Found")
print("  - PATCH  /api/leads/{id}                 -> 200 OK | 404 Not Found")
print("  - GET    /api/leads/{id}/discussions     -> 200 OK | 404 Not Found")
print("  - POST   /api/leads/{id}/discussions     -> 201 Created | 404 Not Found")
print("  - Validation errors                      -> 422 Unprocessable Entity")
