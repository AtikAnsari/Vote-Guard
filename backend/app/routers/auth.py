from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AdminUser, AuditLog
from app.schemas import LoginRequest, SignupRequest, TokenResponse, AdminUserOut
from app.auth import verify_password, hash_password, create_access_token, get_current_admin

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/signup", response_model=TokenResponse)
def signup(signup_req: SignupRequest, request: Request, db: Session = Depends(get_db)):
    """
    Register a new user account with role 'admin' or 'operator'.
    Issues JWT access token and returns dedicated redirect URL.
    """
    client_ip = request.client.host if request.client else "unknown"
    username = signup_req.username.strip().lower()
    role = signup_req.role.strip().lower()

    if role not in ("admin", "operator"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be either 'admin' or 'operator'"
        )

    # Check if username already exists
    existing_user = db.query(AdminUser).filter(AdminUser.username == username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{username}' is already taken. Please choose another or log in."
        )

    # Create new user
    new_user = AdminUser(
        username=username,
        hashed_password=hash_password(signup_req.password),
        full_name=signup_req.full_name.strip(),
        role=role,
        is_active=True
    )
    db.add(new_user)
    db.flush()

    # Log audit event
    audit = AuditLog(
        event_type="USER_REGISTERED",
        status="SUCCESS",
        details=f"New {role} account created for '{username}' ({signup_req.full_name})",
        ip_address=client_ip
    )
    db.add(audit)
    db.commit()

    # Issue JWT token
    token = create_access_token(data={"sub": new_user.username, "role": new_user.role})
    redirect_url = "/admin.html" if role == "admin" else "/operator.html"

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        username=new_user.username,
        full_name=new_user.full_name,
        role=new_user.role,
        redirect_url=redirect_url
    )


@router.post("/login", response_model=TokenResponse)
def login(login_req: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """
    Authenticate a user (admin or operator) and issue a signed JWT access token.
    Returns dedicated redirect_url based on user role.
    """
    client_ip = request.client.host if request.client else "unknown"
    username = login_req.username.strip().lower()

    user = db.query(AdminUser).filter(AdminUser.username == username).first()
    if not user or not verify_password(login_req.password, user.hashed_password):
        # Audit failed login attempt
        audit = AuditLog(
            event_type="LOGIN_FAILED",
            status="DENIED",
            details=f"Failed login attempt for username: '{username}'",
            ip_address=client_ip
        )
        db.add(audit)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    # Issue JWT token
    token = create_access_token(data={"sub": user.username, "role": user.role})
    redirect_url = "/admin.html" if user.role == "admin" else "/operator.html"

    # Audit successful login
    audit = AuditLog(
        event_type="LOGIN_SUCCESS",
        status="SUCCESS",
        details=f"User '{user.username}' ({user.role}) authenticated successfully",
        ip_address=client_ip
    )
    db.add(audit)
    db.commit()

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        username=user.username,
        full_name=user.full_name,
        role=user.role,
        redirect_url=redirect_url
    )


@router.get("/me", response_model=AdminUserOut)
def get_current_user_profile(current_admin: AdminUser = Depends(get_current_admin)):
    """Return the profile of the currently authenticated administrator."""
    return current_admin
