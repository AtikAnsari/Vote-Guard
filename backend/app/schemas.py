from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


# ================= AUTH SCHEMAS =================

class LoginRequest(BaseModel):
    username: str = Field(..., example="admin")
    password: str = Field(..., example="admin123")


class SignupRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, example="operator1")
    password: str = Field(..., min_length=4, max_length=100, example="pass123")
    full_name: str = Field(..., min_length=2, max_length=100, example="Booth Officer")
    role: str = Field(default="operator", example="operator")  # "admin" or "operator"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    full_name: str
    role: str
    redirect_url: str = "/operator.html"


class AdminUserOut(BaseModel):
    id: int
    username: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ================= VOTER CREDENTIAL (2FA / KYC) SCHEMAS =================

class CredentialOut(BaseModel):
    id: int
    aadhar_number: str
    epic_number: str
    full_name: str
    phone_number: Optional[str] = None
    is_assigned: bool
    assigned_rfid_uid: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CredentialCreate(BaseModel):
    aadhar_number: str = Field(..., min_length=12, max_length=16, example="123456789012")
    epic_number: str = Field(..., min_length=5, max_length=20, example="VGD1000001")
    full_name: str = Field(..., min_length=2, max_length=100, example="Rahul Sharma")
    phone_number: Optional[str] = Field(None, example="9876543210")


# ================= VOTER REGISTRATION SCHEMAS =================

class VoterRegisterRequest(BaseModel):
    rfid_uid: str = Field(..., min_length=3, max_length=64, example="E3 2F 91 A4")
    aadhar_number: str = Field(..., min_length=10, max_length=20, example="123456789012")
    epic_number: str = Field(..., min_length=4, max_length=30, example="VGD1000001")
    name: str = Field(..., min_length=2, max_length=100, example="Rahul Sharma")
    phone_number: Optional[str] = Field(None, example="9876543210")


class VoterOut(BaseModel):
    id: int
    voter_code: str
    aadhar_number: str
    name: str
    rfid_uid: str
    has_voted: bool
    voted_at: Optional[datetime] = None
    registered_at: datetime

    class Config:
        from_attributes = True


# ================= VOTING & VERIFICATION SCHEMAS =================

class VoteVerifyRequest(BaseModel):
    rfid_uid: str = Field(..., min_length=2, max_length=64, example="RFID001")


class VoteVerifyResponse(BaseModel):
    event_id: Optional[int] = None
    status: str  # ACCEPTED, ALREADY_VOTED, UNREGISTERED
    message: str
    hardware_led: str  # GREEN, RED, YELLOW
    voter_name: Optional[str] = None
    voter_code: Optional[str] = None
    timestamp: Optional[datetime] = None


class StatsResponse(BaseModel):
    total_voters: int
    votes_recorded: int
    pending_votes: int
    fraud_attempts: int
    available_credentials: int


# ================= AUDIT LOG SCHEMAS =================

class AuditLogOut(BaseModel):
    id: int
    event_type: str
    rfid_uid: Optional[str] = None
    voter_id: Optional[int] = None
    status: str
    details: str
    ip_address: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True
