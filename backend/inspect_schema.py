"""
Inspect the actual database schema using SQLAlchemy.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import inspect
from app.database import engine
from app.models import Lead, Discussion

inspector = inspect(engine)

print("=" * 60)
print("DATABASE SCHEMA INSPECTION")
print("=" * 60)

for table_name in ['leads', 'discussions']:
    print(f"\nTable: {table_name}")
    print("-" * 60)

    # Get columns
    columns = inspector.get_columns(table_name)
    print("\nColumns:")
    for col in columns:
        nullable = "NULL" if col['nullable'] else "NOT NULL"
        default = f" DEFAULT {col['default']}" if col.get('default') else ""
        print(f"  {col['name']:20} {str(col['type']):15} {nullable}{default}")

    # Get primary keys
    pk = inspector.get_pk_constraint(table_name)
    print(f"\nPrimary Key: {', '.join(pk['constrained_columns'])}")

    # Get foreign keys
    fks = inspector.get_foreign_keys(table_name)
    if fks:
        print("\nForeign Keys:")
        for fk in fks:
            print(f"  {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
            print(f"    ondelete: {fk.get('ondelete', 'NO ACTION')}")

    # Get indexes
    indexes = inspector.get_indexes(table_name)
    if indexes:
        print("\nIndexes:")
        for idx in indexes:
            print(f"  {idx['name']}: {idx['column_names']}")

print("\n" + "=" * 60)
print("RELATIONSHIP VERIFICATION")
print("=" * 60)

print("\nLead model:")
print(f"  - Table: {Lead.__tablename__}")
print(f"  - Relationships: {list(Lead.__mapper__.relationships.keys())}")

print("\nDiscussion model:")
print(f"  - Table: {Discussion.__tablename__}")
print(f"  - Relationships: {list(Discussion.__mapper__.relationships.keys())}")

print("\n" + "=" * 60)
print("SCHEMA VERIFICATION COMPLETE")
print("=" * 60)
