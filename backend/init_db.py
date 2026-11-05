"""
VOTE-GUARD Database Initialization Script
Idempotently creates all tables in MySQL 'vote_guard' using SQLAlchemy metadata.
Seeds default administrator and operator accounts without any dummy data.
"""

import sys
import os
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.database import engine, SessionLocal
from app.models import Base, AdminUser, VoterCredential, Voter, AuditLog
from app.auth import hash_password


def init_database():
    print("=" * 60)
    print("VOTE-GUARD: Initializing Clean Production Database Schema...")
    print("=" * 60)

    # 1. Create tables safely (non-destructive: CREATE TABLE IF NOT EXISTS)
    Base.metadata.create_all(bind=engine)
    print("[OK] Tables verified/created: admin_users, voter_credentials, voters, audit_logs")

    db = SessionLocal()
    try:
        # 2. Seed Default Administrator if not exists
        admin = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if not admin:
            admin = AdminUser(
                username="admin",
                hashed_password=hash_password("admin123"),
                full_name="System Administrator",
                role="admin",
                is_active=True
            )
            db.add(admin)
            db.commit()
            print("[OK] Default Administrator created: username='admin', password='admin123'")
        else:
            print(f"[OK] Existing Administrator detected: '{admin.username}'")

        # 3. Seed Default Operator if not exists
        operator_user = db.query(AdminUser).filter(AdminUser.username == "operator").first()
        if not operator_user:
            operator_user = AdminUser(
                username="operator",
                hashed_password=hash_password("operator123"),
                full_name="Booth Polling Officer",
                role="operator",
                is_active=True
            )
            db.add(operator_user)
            db.commit()
            print("[OK] Default Operator created: username='operator', password='operator123'")
        else:
            print(f"[OK] Existing Operator detected: '{operator_user.username}'")

        print("[OK] Zero mock/dummy data seeded. Database is pristine for physical hardware.")

    finally:
        db.close()

    print("=" * 60)
    print("VOTE-GUARD Database is 100% READY.")
    print("=" * 60)


if __name__ == "__main__":
    init_database()
