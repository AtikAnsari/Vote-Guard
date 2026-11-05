import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import update, desc
from app.database import get_db
from app.models import Voter, AuditLog
from app.schemas import VoteVerifyRequest, VoteVerifyResponse

router = APIRouter(prefix="/api/vote", tags=["Voting & Verification"])

# In-memory latest scan event tracker for live wireless receiver synchronization
scan_counter = 0
latest_scan_event: Dict[str, Any] = {
    "event_id": 0,
    "status": "IDLE",
    "hardware_led": "IDLE",
    "message": "Ready for scan",
    "voter_name": None,
    "voter_code": None,
    "timestamp": None
}

# In-memory bounce shield for recently accepted votes: { normalized_uid: timestamp_seconds }
recent_accepted_votes: Dict[str, float] = {}


@router.post("/verify", response_model=VoteVerifyResponse)
@router.post("/verify-and-record", response_model=VoteVerifyResponse)
def verify_and_record_vote(
    payload: VoteVerifyRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Kiosk / Polling Station endpoint for RFID vote verification.
    Triggered directly by ESP32 RFID receiver or booth terminal.
    Applies atomic conditional row update to eliminate race conditions.
    Maps status to ESP32 hardware directives (GREEN, RED, YELLOW).
    """
    global scan_counter, latest_scan_event, recent_accepted_votes

    client_ip = request.client.host if request.client else "kiosk"
    normalized_uid = payload.rfid_uid.replace(" ", "").replace(":", "").strip().upper()
    now_ts = time.time()
    now = datetime.utcnow()

    # 0. BOUNCE SHIELD: Check if this card was JUST accepted within the last 4.0 seconds (prevents serial echo / dual-path bounce)
    if normalized_uid in recent_accepted_votes:
        time_since_vote = now_ts - recent_accepted_votes[normalized_uid]
        if time_since_vote < 4.0:
            voter = db.query(Voter).filter(Voter.rfid_uid == normalized_uid).first()
            return VoteVerifyResponse(
                event_id=scan_counter,
                status="ACCEPTED",
                message="✅ Voter Verified Successfully. Vote recorded.",
                hardware_led="GREEN",
                voter_name=voter.name if voter else None,
                voter_code=voter.voter_code if voter else None,
                timestamp=voter.voted_at if voter else now
            )
        else:
            recent_accepted_votes.pop(normalized_uid, None)

    # 1. ATOMIC CONDITIONAL UPDATE:
    # Only updates if has_voted is currently FALSE.
    # MySQL row write-lock ensures concurrent duplicate requests cannot race.
    stmt = (
        update(Voter)
        .where(Voter.rfid_uid == normalized_uid, Voter.has_voted == False)
        .values(has_voted=True, voted_at=now)
    )
    result = db.execute(stmt)

    if result.rowcount == 1:
        # EXACTLY-ONCE SUCCESS (VOTE IS DONE)
        recent_accepted_votes[normalized_uid] = now_ts
        voter = db.query(Voter).filter(Voter.rfid_uid == normalized_uid).first()
        audit = AuditLog(
            event_type="VOTE_ACCEPTED",
            rfid_uid=normalized_uid,
            voter_id=voter.id if voter else None,
            status="SUCCESS",
            details=f"Vote recorded for {voter.name} ({voter.voter_code}) with UID {normalized_uid}",
            ip_address=client_ip,
            timestamp=now
        )
        db.add(audit)
        db.commit()

        scan_counter += 1
        resp = VoteVerifyResponse(
            event_id=scan_counter,
            status="ACCEPTED",
            message="✅ Voter Verified Successfully. Vote recorded.",
            hardware_led="GREEN",
            voter_name=voter.name,
            voter_code=voter.voter_code,
            timestamp=now
        )

        latest_scan_event = {
            "event_id": scan_counter,
            "status": "ACCEPTED",
            "hardware_led": "GREEN",
            "message": resp.message,
            "voter_name": voter.name,
            "voter_code": voter.voter_code,
            "rfid_uid": normalized_uid,
            "timestamp": now.isoformat()
        }

        return resp

    # 2. EVALUATE REJECTION (DUPLICATE vs UNREGISTERED)
    voter = db.query(Voter).filter(Voter.rfid_uid == normalized_uid).first()

    if voter:
        # Check if this is a rapid duplicate/bounce of a vote that was JUST accepted within the last 4.0 seconds
        if voter.voted_at and abs((now - voter.voted_at).total_seconds()) < 4.0:
            return VoteVerifyResponse(
                event_id=scan_counter,
                status="ACCEPTED",
                message="✅ Voter Verified Successfully. Vote recorded.",
                hardware_led="GREEN",
                voter_name=voter.name,
                voter_code=voter.voter_code,
                timestamp=voter.voted_at
            )

        # GENUINE DUPLICATE ATTEMPT: Voter exists, and voted more than 4.0 seconds ago
        audit = AuditLog(
            event_type="DUPLICATE_ATTEMPT",
            rfid_uid=normalized_uid,
            voter_id=voter.id,
            status="WARNING",
            details=f"Duplicate vote attempt blocked for {voter.name} ({voter.voter_code}) with UID {normalized_uid}",
            ip_address=client_ip,
            timestamp=now
        )
        db.add(audit)
        db.commit()

        scan_counter += 1
        resp = VoteVerifyResponse(
            event_id=scan_counter,
            status="ALREADY_VOTED",
            message="🚨 Duplicate Voting Detected! Vote blocked.",
            hardware_led="RED",
            voter_name=voter.name,
            voter_code=voter.voter_code,
            timestamp=voter.voted_at
        )

        latest_scan_event = {
            "event_id": scan_counter,
            "status": "ALREADY_VOTED",
            "hardware_led": "RED",
            "message": resp.message,
            "voter_name": voter.name,
            "voter_code": voter.voter_code,
            "rfid_uid": normalized_uid,
            "timestamp": now.isoformat()
        }

        return resp
    else:
        # UNREGISTERED CARD
        audit = AuditLog(
            event_type="UNREGISTERED_CARD",
            rfid_uid=normalized_uid,
            voter_id=None,
            status="DENIED",
            details=f"Unregistered RFID card presented: {normalized_uid}",
            ip_address=client_ip,
            timestamp=now
        )
        db.add(audit)
        db.commit()

        scan_counter += 1
        resp = VoteVerifyResponse(
            event_id=scan_counter,
            status="UNREGISTERED",
            message="❌ Voter is not registered. Access denied.",
            hardware_led="YELLOW",
            voter_name=None,
            voter_code=None,
            timestamp=None
        )

        latest_scan_event = {
            "event_id": scan_counter,
            "status": "UNREGISTERED",
            "hardware_led": "YELLOW",
            "message": resp.message,
            "voter_name": None,
            "voter_code": None,
            "rfid_uid": normalized_uid,
            "timestamp": now.isoformat()
        }

        return resp


@router.get("/latest-event")
def get_latest_scan_event():
    """
    Polling endpoint for the Operator Terminal.
    Returns the most recent RFID scan event triggered by the hardware receiver.
    """
    return latest_scan_event


@router.get("/history")
def get_recent_verification_history(db: Session = Depends(get_db)):
    """Return the 10 most recent verification events for display on the polling station UI."""
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.event_type.in_(["VOTE_ACCEPTED", "DUPLICATE_ATTEMPT", "UNREGISTERED_CARD"]))
        .order_by(desc(AuditLog.id))
        .limit(10)
        .all()
    )

    activities = []
    for log in logs:
        voter_code = log.voter.voter_code if log.voter else "N/A"
        name = log.voter.name if log.voter else "Unknown Voter"

        if log.event_type == "VOTE_ACCEPTED":
            status_text = "Voted"
            verification = "Valid"
        elif log.event_type == "DUPLICATE_ATTEMPT":
            status_text = "Voted"
            verification = "Duplicate"
        else:
            status_text = "Rejected"
            verification = "Not Registered"

        activities.append({
            "id": log.id,
            "voterId": voter_code,
            "name": name,
            "rfid": log.rfid_uid or "N/A",
            "status": status_text,
            "verification": verification,
            "time": log.timestamp.strftime("%I:%M %p") if log.timestamp else ""
        })

    return activities


@router.get("/recorded-rfids")
def get_recorded_rfids(db: Session = Depends(get_db)):
    """Return the list of RFID UIDs that have already cast their vote."""
    records = db.query(Voter.rfid_uid).filter(Voter.has_voted == True).all()
    return [r[0] for r in records]


@router.get("/public-stats")
def get_public_stats(db: Session = Depends(get_db)):
    """Public statistical metrics for the polling station kiosk."""
    total = db.query(Voter).count()
    voted = db.query(Voter).filter(Voter.has_voted == True).count()
    pending = total - voted
    fraud = db.query(AuditLog).filter(AuditLog.event_type == "DUPLICATE_ATTEMPT").count()

    return {
        "total_voters": total,
        "votes_recorded": voted,
        "pending_votes": pending,
        "fraud_attempts": fraud
    }
