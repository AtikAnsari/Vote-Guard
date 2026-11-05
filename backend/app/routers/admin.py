from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models import AdminUser, Voter, VoterCredential, AuditLog
from app.schemas import (
    VoterRegisterRequest,
    VoterOut,
    CredentialOut,
    CredentialCreate,
    StatsResponse,
    AuditLogOut
)
from app.auth import get_current_admin

router = APIRouter(prefix="/api/admin", tags=["Admin Operations"])


@router.get("/stats", response_model=StatsResponse)
def get_admin_dashboard_stats(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Return comprehensive system statistics for the admin dashboard."""
    total = db.query(Voter).count()
    voted = db.query(Voter).filter(Voter.has_voted == True).count()
    pending = total - voted
    fraud = db.query(AuditLog).filter(AuditLog.event_type == "DUPLICATE_ATTEMPT").count()
    available_creds = db.query(VoterCredential).filter(VoterCredential.is_assigned == False).count()

    return StatsResponse(
        total_voters=total,
        votes_recorded=voted,
        pending_votes=pending,
        fraud_attempts=fraud,
        available_credentials=available_creds
    )


@router.get("/voters", response_model=List[VoterOut])
def list_voters(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Retrieve all registered voters with their vote status."""
    return db.query(Voter).order_by(desc(Voter.id)).all()


@router.get("/credentials", response_model=List[CredentialOut])
def list_credentials(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """List pre-authorized government/KYC credentials and their UID assignment status."""
    return db.query(VoterCredential).order_by(VoterCredential.is_assigned, VoterCredential.id).all()


@router.post("/credentials", response_model=CredentialOut)
def create_credential(
    payload: CredentialCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Add a new pre-authorized Aadhaar/EPIC credential for 2FA validation."""
    clean_aadhar = payload.aadhar_number.strip().replace(" ", "").replace("-", "")
    clean_epic = payload.epic_number.strip().upper()

    existing = db.query(VoterCredential).filter(
        (VoterCredential.aadhar_number == clean_aadhar) | (VoterCredential.epic_number == clean_epic)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Credential with this Aadhaar or Election Card number already exists."
        )

    cred = VoterCredential(
        aadhar_number=clean_aadhar,
        epic_number=clean_epic,
        full_name=payload.full_name.strip(),
        phone_number=payload.phone_number.strip() if payload.phone_number else None,
        is_assigned=False
    )
    db.add(cred)
    db.commit()
    db.refresh(cred)
    return cred


@router.post("/voters", response_model=VoterOut)
def register_voter_with_2fa(
    payload: VoterRegisterRequest,
    request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """
    Register a voter with 2FA credential validation.
    Enforces that:
    1. The RFID UID is not already registered.
    2. The Aadhaar or Election Card (EPIC) credentials have not already been assigned to another UID.
    """
    client_ip = request.client.host if request.client else "admin"
    clean_uid = payload.rfid_uid.replace(" ", "").replace(":", "").strip().upper()
    clean_aadhar = payload.aadhar_number.strip().replace(" ", "").replace("-", "")
    clean_epic = payload.epic_number.strip().upper()
    clean_name = payload.name.strip()

    # 1. Check if RFID UID is already registered in voters or assigned in credentials
    existing_voter_by_uid = db.query(Voter).filter(Voter.rfid_uid == clean_uid).first()
    if existing_voter_by_uid:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"RFID Conflict: Tag '{clean_uid}' is ALREADY registered to voter '{existing_voter_by_uid.name}' ({existing_voter_by_uid.voter_code})!"
        )

    existing_cred_by_uid = db.query(VoterCredential).filter(VoterCredential.assigned_rfid_uid == clean_uid).first()
    if existing_cred_by_uid:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"RFID Conflict: Tag '{clean_uid}' is ALREADY assigned to citizen '{existing_cred_by_uid.full_name}' (EPIC: {existing_cred_by_uid.epic_number})!"
        )

    # 2. Check if voter code / EPIC is already used in voters table
    existing_voter_by_code = db.query(Voter).filter(Voter.voter_code == clean_epic).first()
    if existing_voter_by_code:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Election Card Conflict: Card '{clean_epic}' is already registered to '{existing_voter_by_code.name}' with UID '{existing_voter_by_code.rfid_uid}'!"
        )

    # 3. Check 2FA Credentials table
    cred = db.query(VoterCredential).filter(
        (VoterCredential.aadhar_number == clean_aadhar) | (VoterCredential.epic_number == clean_epic)
    ).first()

    if cred:
        # Check if already assigned
        if cred.is_assigned and cred.assigned_rfid_uid:
            # Audit rejected registration attempt
            audit = AuditLog(
                event_type="REGISTRATION_REJECTED",
                rfid_uid=clean_uid,
                status="DENIED",
                details=f"2FA Conflict: Aadhaar/EPIC already assigned to UID '{cred.assigned_rfid_uid}' (Voter: {cred.full_name})",
                ip_address=client_ip
            )
            db.add(audit)
            db.commit()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"2FA Conflict: These credentials (Aadhaar: {clean_aadhar[-4:]} / EPIC: {clean_epic}) are ALREADY used and assigned to RFID UID '{cred.assigned_rfid_uid}' (Voter: {cred.full_name}). Multiple UIDs cannot be assigned to the same citizen credentials!"
            )
        else:
            # Mark existing credential as assigned
            cred.is_assigned = True
            cred.assigned_rfid_uid = clean_uid
            if not cred.full_name and clean_name:
                cred.full_name = clean_name
    else:
        # Create new credential record and assign
        cred = VoterCredential(
            aadhar_number=clean_aadhar,
            epic_number=clean_epic,
            full_name=clean_name,
            phone_number=payload.phone_number.strip() if payload.phone_number else None,
            is_assigned=True,
            assigned_rfid_uid=clean_uid
        )
        db.add(cred)
        try:
            db.flush()
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Registration Conflict: Duplicate entry or constraint violation ({str(e)})."
            )

    # 4. Insert Voter
    new_voter = Voter(
        voter_code=clean_epic,
        aadhar_number=clean_aadhar,
        name=clean_name,
        rfid_uid=clean_uid,
        credential_id=cred.id,
        has_voted=False
    )
    db.add(new_voter)
    try:
        db.flush()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Registration Conflict: Could not register voter ({str(e)})."
        )

    # 5. Audit Log
    audit = AuditLog(
        event_type="VOTER_REGISTERED",
        rfid_uid=clean_uid,
        voter_id=new_voter.id,
        status="SUCCESS",
        details=f"Admin '{admin.username}' registered voter '{clean_name}' (EPIC: {clean_epic}) to RFID '{clean_uid}'",
        ip_address=client_ip
    )
    db.add(audit)
    db.commit()
    db.refresh(new_voter)

    return new_voter


@router.get("/audit-logs", response_model=List[AuditLogOut])
def list_audit_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Retrieve persistent audit log entries."""
    return db.query(AuditLog).order_by(desc(AuditLog.id)).limit(limit).all()


@router.post("/reset-votes")
def reset_all_votes_for_testing(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Reset voting flags on registered voters for test/demo repetitions without deleting records."""
    from app.routers.voting import recent_accepted_votes
    recent_accepted_votes.clear()
    db.query(Voter).update({Voter.has_voted: False, Voter.voted_at: None})
    audit = AuditLog(
        event_type="RESET_VOTES",
        status="INFO",
        details=f"Admin '{admin.username}' reset all voting statuses for testing",
        ip_address="admin"
    )
    db.add(audit)
    db.commit()
    return {"message": "All voting flags reset to Not Voted."}
