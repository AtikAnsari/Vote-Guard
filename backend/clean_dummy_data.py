"""
VOTE-GUARD Database Purge Script
Removes all dummy voter records, mock 2FA credentials, and test audit logs.
Preserves administrative user accounts (admin and operator).
"""

import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.database import engine, SessionLocal
from app.models import Voter, VoterCredential, AuditLog, AdminUser
from app.auth import hash_password
from sqlalchemy import text


def purge_dummy_data():
    print("=" * 60)
    print("PURGING ALL DUMMY DATA FROM VOTE-GUARD DATABASE")
    print("=" * 60)

    db = SessionLocal()
    try:
        # 1. Clear voters
        deleted_voters = db.query(Voter).delete()
        print(f"[CLEARED] Removed {deleted_voters} dummy voter records.")

        # 2. Clear voter credentials
        deleted_creds = db.query(VoterCredential).delete()
        print(f"[CLEARED] Removed {deleted_creds} dummy 2FA KYC credentials.")

        # 3. Clear test audit logs
        deleted_logs = db.query(AuditLog).delete()
        print(f"[CLEARED] Removed {deleted_logs} test audit log entries.")

        # 4. Verify admin and operator accounts exist
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
            print("[CREATED] Admin account: username='admin', password='admin123'")

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
            print("[CREATED] Operator account: username='operator', password='operator123'")

        # 5. Add clean initialization audit record
        clean_log = AuditLog(
            event_type="SYSTEM_READY",
            status="SUCCESS",
            details="All mock data purged. System initialized for live ESP32 hardware prototype integration.",
            ip_address="127.0.0.1"
        )
        db.add(clean_log)
        db.commit()

        print("=" * 60)
        print("DATABASE IS NOW 100% CLEAN & READY FOR HARDWARE RFID TAGS!")
        print("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    purge_dummy_data()

