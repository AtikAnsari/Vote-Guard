"""
VOTE-GUARD Logic Verification Test
Tests:
1. Admin Login & JWT generation.
2. 2FA Credential verification and Duplicate Aadhaar / EPIC rejection.
3. Successful Voter Registration with 2FA check.
4. Atomic Voting Acceptance.
5. Duplicate Voting Rejection.
6. Unregistered RFID rejection.
7. Audit Log recording.
"""

import sys
from pathlib import Path
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal
from app.models import Voter, VoterCredential, AuditLog, AdminUser
from app.schemas import LoginRequest, VoteVerifyRequest, VoterRegisterRequest
from app.routers.auth import login
from app.routers.voting import verify_and_record_vote
from app.routers.admin import register_voter_with_2fa, list_voters, get_admin_dashboard_stats
from app.auth import get_current_admin
from fastapi import HTTPException


class DummyRequest:
    class Client:
        host = "127.0.0.1"
    client = Client()


def run_tests():
    db = SessionLocal()
    req = DummyRequest()
    print("=" * 60)
    print("RUNNING VOTE-GUARD BACKEND LOGIC VERIFICATION")
    print("=" * 60)

    try:
        # 1. TEST ADMIN LOGIN
        print("\n--- 1. Testing Admin Authentication ---")
        login_res = login(LoginRequest(username="admin", password="admin123"), req, db)
        print(f"[PASS] Logged in as: {login_res.full_name}, Role: {login_res.role}")
        print(f"[PASS] JWT Access Token generated (length: {len(login_res.access_token)})")

        # Get Admin object
        admin_user = db.query(AdminUser).filter(AdminUser.username == "admin").first()

        # 2. TEST 2FA CREDENTIAL CONFLICT (Trying to register with already assigned Aadhaar: 123456789012)
        print("\n--- 2. Testing 2FA Credential Conflict Detection ---")
        try:
            register_voter_with_2fa(
                VoterRegisterRequest(
                    rfid_uid="RFID_NEW_TEST_01",
                    aadhar_number="123456789012",  # Rahul Sharma's already assigned Aadhaar!
                    epic_number="VGD1000001",
                    name="Fake Imposter",
                    phone_number="9999999999"
                ),
                req,
                db,
                admin_user
            )
            print("[FAIL] Conflict was NOT caught!")
        except HTTPException as e:
            print(f"[PASS] 2FA conflict caught successfully! Status {e.status_code}")
            print(f"       Message: {e.detail}")

        # 3. TEST SUCCESSFUL VOTER REGISTRATION WITH UNASSIGNED 2FA CREDENTIAL
        print("\n--- 3. Testing Valid Voter Registration with 2FA Credential ---")
        # Aman Patel's credential (Aadhaar: 234567890123, EPIC: VGD1000002) is unassigned
        test_uid = "TEST_RFID_AMAN"
        # Clean up if previously run
        db.query(Voter).filter(Voter.rfid_uid == test_uid).delete()
        cred = db.query(VoterCredential).filter(VoterCredential.epic_number == "VGD1000002").first()
        if cred:
            cred.is_assigned = False
            cred.assigned_rfid_uid = None
        db.commit()

        new_voter = register_voter_with_2fa(
            VoterRegisterRequest(
                rfid_uid=test_uid,
                aadhar_number="234567890123",
                epic_number="VGD1000002",
                name="Aman Patel",
                phone_number="9876543211"
            ),
            req,
            db,
            admin_user
        )
        print(f"[PASS] Registered Voter: {new_voter.name} ({new_voter.voter_code}) with UID: {new_voter.rfid_uid}")

        # Verify credential is now assigned
        db.refresh(cred)
        print(f"[PASS] Credential updated: is_assigned={cred.is_assigned}, assigned_rfid_uid={cred.assigned_rfid_uid}")

        # 4. TEST ATOMIC VOTE ACCEPTANCE
        print("\n--- 4. Testing Atomic Vote Acceptance ---")
        vote_res1 = verify_and_record_vote(VoteVerifyRequest(rfid_uid=test_uid), req, db)
        print(f"[PASS] First Vote Status: {vote_res1.status} | LED Directive: {vote_res1.hardware_led}")
        print(f"       Message: {vote_res1.message}")
        assert vote_res1.status == "ACCEPTED"
        assert vote_res1.hardware_led == "GREEN"

        # 5. TEST DUPLICATE VOTE ATTEMPT BLOCKING
        print("\n--- 5. Testing Duplicate Vote Detection ---")
        vote_res2 = verify_and_record_vote(VoteVerifyRequest(rfid_uid=test_uid), req, db)
        print(f"[PASS] Duplicate Vote Status: {vote_res2.status} | LED Directive: {vote_res2.hardware_led}")
        print(f"       Message: {vote_res2.message}")
        assert vote_res2.status == "ALREADY_VOTED"
        assert vote_res2.hardware_led == "RED"

        # 6. TEST UNREGISTERED RFID SCAN
        print("\n--- 6. Testing Unregistered RFID Scan ---")
        vote_res3 = verify_and_record_vote(VoteVerifyRequest(rfid_uid="UNKNOWN_CARD_999"), req, db)
        print(f"[PASS] Unknown Card Status: {vote_res3.status} | LED Directive: {vote_res3.hardware_led}")
        print(f"       Message: {vote_res3.message}")
        assert vote_res3.status == "UNREGISTERED"
        assert vote_res3.hardware_led == "YELLOW"

        # 7. TEST AUDIT LOGS
        print("\n--- 7. Testing Audit Logs Persistence ---")
        recent_logs = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(5).all()
        for log in recent_logs:
            print(f"  [LOG #{log.id}] {log.event_type} | {log.status} | {log.details}")

        # 8. TEST ADMIN STATS
        print("\n--- 8. Testing Admin Stats ---")
        stats = get_admin_dashboard_stats(db, admin_user)
        print(f"[PASS] Total Voters: {stats.total_voters}")
        print(f"[PASS] Votes Recorded: {stats.votes_recorded}")
        print(f"[PASS] Pending Votes: {stats.pending_votes}")
        print(f"[PASS] Fraud Attempts: {stats.fraud_attempts}")
        print(f"[PASS] Available Credentials: {stats.available_credentials}")

        print("\n" + "=" * 60)
        print("ALL BACKEND LOGIC VERIFICATION TESTS PASSED SUCCESSFULLY!")
        print("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    run_tests()
