"""
Verification script for database setup.

Tests that the database module can be imported and the engine can connect.
"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.database import engine, SessionLocal, Base, get_db, DATABASE_URL

    print("[OK] Database module imported successfully")
    print(f"[OK] Database URL: {DATABASE_URL}")

    # Test creating a session
    db = SessionLocal()
    print("[OK] Session created successfully")
    db.close()
    print("[OK] Session closed successfully")

    # Test the get_db generator
    db_gen = get_db()
    db = next(db_gen)
    print("[OK] get_db() dependency generator works")
    try:
        db_gen.close()
    except StopIteration:
        pass

    # Test engine connection
    with engine.connect() as connection:
        print("[OK] Database engine connection successful")

    print("\n[SUCCESS] All database setup checks passed!")
    print("\nConfiguration summary:")
    print(f"  - Engine: {engine}")
    print(f"  - Dialect: {engine.dialect.name}")
    print(f"  - Session factory: {SessionLocal}")
    print(f"  - Base class: {Base}")

except Exception as e:
    print(f"\n[FAIL] Database setup verification failed:")
    print(f"   {type(e).__name__}: {e}")
    sys.exit(1)
