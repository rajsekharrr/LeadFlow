"""
Demonstrate the separation between ORM models and Pydantic schemas.

Shows how the two layers work together while remaining independent.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models import Lead, Discussion
from app.schemas import (
    CreateLeadRequest,
    LeadResponse,
    CreateDiscussionRequest,
    DiscussionResponse,
    LeadStatus
)
from app.database import SessionLocal, Base, engine

print("=" * 70)
print("ORM MODELS vs PYDANTIC SCHEMAS - SEPARATION DEMONSTRATION")
print("=" * 70)

# Create database
Base.metadata.create_all(bind=engine)
db = SessionLocal()

print("\n[SCENARIO 1] Creating a Lead: Request Schema -> ORM Model")
print("-" * 70)

# Step 1: Client sends JSON, validated by Pydantic schema
request_data = {
    "name": "Alice Johnson",
    "company": "TechStart Inc",
    "phone": "+1-555-0199",
    "status": "Contacted"
}

# Pydantic validates the request
create_request = CreateLeadRequest(**request_data)
print(f"[1] Request validated by Pydantic: {create_request.model_dump()}")

# Step 2: Convert Pydantic schema to ORM model
# This is what happens in crud.py
lead = Lead(
    name=create_request.name,
    company=create_request.company,
    phone=create_request.phone,
    status=create_request.status.value  # Enum -> string
)
db.add(lead)
db.commit()
db.refresh(lead)

print(f"[2] ORM model created in database: {lead}")
print(f"    Database columns: {[c.name for c in Lead.__table__.columns]}")

print("\n[SCENARIO 2] Returning a Lead: ORM Model -> Response Schema")
print("-" * 70)

# Step 3: Simulate adding computed fields (normally done in crud.py)
# These fields DON'T exist in the database!
lead.last_note = "Had initial call, very interested"
lead.last_discussion_at = None
lead.discussion_count = 0

print(f"[3] ORM object with computed fields added:")
print(f"    Database fields: name={lead.name}, status={lead.status}")
print(f"    Computed fields: last_note={lead.last_note}, discussion_count={lead.discussion_count}")

# Step 4: Convert ORM model to Pydantic response schema
# from_attributes=True allows reading from object attributes
response = LeadResponse.model_validate(lead)
print(f"[4] Response schema created from ORM object:")
print(f"    Response contains: {response.model_dump().keys()}")
print(f"    JSON output: {response.model_dump_json()[:100]}...")

print("\n[SCENARIO 3] Schema Fields vs Database Columns")
print("-" * 70)

# Compare what's in the schema vs what's in the database
lead_response_fields = set(LeadResponse.model_fields.keys())
lead_db_columns = set([c.name for c in Lead.__table__.columns])

print(f"[5] LeadResponse schema fields: {sorted(lead_response_fields)}")
print(f"[6] Lead database columns: {sorted(lead_db_columns)}")

computed_fields = lead_response_fields - lead_db_columns
database_only = lead_db_columns - lead_response_fields
shared_fields = lead_response_fields & lead_db_columns

print(f"\n    Fields in schema but NOT in database (computed):")
print(f"      {sorted(computed_fields)}")
print(f"    Fields in database but NOT in schema:")
print(f"      {sorted(database_only) if database_only else '(none)'}")
print(f"    Shared fields:")
print(f"      {sorted(shared_fields)}")

print("\n[SCENARIO 4] Input Schema vs Response Schema Differences")
print("-" * 70)

create_fields = set(CreateLeadRequest.model_fields.keys())
response_fields = set(LeadResponse.model_fields.keys())

print(f"[7] CreateLeadRequest fields: {sorted(create_fields)}")
print(f"[8] LeadResponse fields: {sorted(response_fields)}")

client_cannot_set = response_fields - create_fields
client_must_provide = create_fields - response_fields

print(f"\n    Fields client receives but CANNOT set (system-managed):")
print(f"      {sorted(client_cannot_set)}")
print(f"    Fields in create request not returned:")
print(f"      {sorted(client_must_provide) if client_must_provide else '(none - all included in response)'}")

print("\n[SCENARIO 5] Validation: Pydantic Catches Errors ORM Doesn't")
print("-" * 70)

# ORM allows invalid status (it's just a string column)
try:
    invalid_lead = Lead(name="Test", status="InvalidStatus")
    print(f"[9] ORM accepts invalid status: {invalid_lead.status}")
    print("    (ORM doesn't validate - it's just a VARCHAR column)")
except Exception as e:
    print(f"[9] ORM rejected: {e}")

# Pydantic rejects invalid status
try:
    from pydantic import ValidationError
    invalid_request = CreateLeadRequest(name="Test", status="InvalidStatus")
    print(f"[10] Pydantic should have rejected invalid status!")
except ValidationError as e:
    print(f"[10] Pydantic rejected invalid status (as expected)")
    print(f"     Validation error: {e.errors()[0]['msg']}")

print("\n[SCENARIO 6] Why Separation Matters: Independent Evolution")
print("-" * 70)

print("""
[11] Example: Adding a new computed field to the API

   Database (ORM):        | API (Pydantic):
   - No change needed     | - Add 'days_since_last_contact' to LeadResponse
   - Lead table unchanged | - Compute in crud.py before returning
                         | - Client gets new field automatically

[12] Example: Removing a field from the API

   Database (ORM):        | API (Pydantic):
   - Keep phone column    | - Remove 'phone' from CreateLeadRequest
   - Old data preserved   | - Remove 'phone' from LeadResponse
   - Can query if needed  | - Client never sees it

[13] Example: Changing validation rules

   Database (ORM):        | API (Pydantic):
   - No change            | - Add max_length=100 to 'name' field
                         | - Add regex pattern to 'phone' field
                         | - Database constraint unchanged
""")

# Clean up
db.delete(lead)
db.commit()
db.close()

print("\n" + "=" * 70)
print("[SUCCESS] ORM/Schema separation demonstration complete!")
print("=" * 70)

print("\nKey Takeaways:")
print("  1. ORM models = Database contract (tables, columns, relationships)")
print("  2. Pydantic schemas = API contract (validation, serialization)")
print("  3. Response schemas can include computed fields not in database")
print("  4. Pydantic validates; ORM just stores (validation is optional)")
print("  5. Changes to one layer don't require changes to the other")
print("  6. from_attributes=True bridges the gap: ORM object -> Pydantic schema")
