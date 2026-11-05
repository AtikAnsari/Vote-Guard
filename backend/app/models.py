from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base


class AdminUser(Base):
    """Administrative user model with RBAC role."""
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), default="admin", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class VoterCredential(Base):
    """
    Pre-authorized or government electoral identity / KYC credentials.
    Acts as a 2FA credential verification layer:
    Ensures an Aadhaar number or Election Card (EPIC) can only ever be assigned to ONE RFID UID.
    """
    __tablename__ = "voter_credentials"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    aadhar_number = Column(String(20), unique=True, index=True, nullable=False)
    epic_number = Column(String(30), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    date_of_birth = Column(String(20), nullable=True)
    phone_number = Column(String(15), nullable=True)
    is_assigned = Column(Boolean, default=False, nullable=False)
    assigned_rfid_uid = Column(String(64), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    voter = relationship("Voter", back_populates="credential", uselist=False)


class Voter(Base):
    """
    Registered voter entity bound to an RFID UID.
    Stores exactly-once voting status and timestamps.
    """
    __tablename__ = "voters"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    voter_code = Column(String(50), unique=True, index=True, nullable=False)  # Usually EPIC number
    aadhar_number = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    rfid_uid = Column(String(64), unique=True, index=True, nullable=False)
    credential_id = Column(Integer, ForeignKey("voter_credentials.id", ondelete="SET NULL"), nullable=True)
    has_voted = Column(Boolean, default=False, nullable=False)
    voted_at = Column(DateTime, nullable=True)
    registered_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    credential = relationship("VoterCredential", back_populates="voter")
    audit_logs = relationship("AuditLog", back_populates="voter")


class AuditLog(Base):
    """
    Persistent and tamper-evident audit log for all system events:
    votes, duplicate attempts, unregistered scans, admin logins, and registrations.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    event_type = Column(String(50), nullable=False, index=True)
    rfid_uid = Column(String(64), nullable=True, index=True)
    voter_id = Column(Integer, ForeignKey("voters.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(30), nullable=False)  # SUCCESS, WARNING, DENIED, INFO
    details = Column(String(255), nullable=False)
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    voter = relationship("Voter", back_populates="audit_logs")
