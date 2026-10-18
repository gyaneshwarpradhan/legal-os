from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import (
    get_client_ip,
    get_current_active_user,
    get_db,
    require_role,
)
from app.core.exceptions import AuthenticationError
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.audit_service import log_action
from app.services.auth_service import authenticate_user, create_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    request: Request,
    credentials: LoginRequest,
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, credentials.email, credentials.password)
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("user-agent")

    if not user:
        log_action(
            db,
            organization_id=getattr(user, "organization_id", None),
            action="login_failed",
            details={"email": credentials.email},
            ip_address=client_ip,
            user_agent=user_agent,
        )
        raise AuthenticationError(detail="Incorrect email or password")

    if not user.is_active:
        raise AuthenticationError(detail="User account is deactivated")

    # Issue token
    access_token = create_access_token(
        data={"sub": str(user.id), "org": str(user.organization_id)}
    )

    # Log successful login
    log_action(
        db,
        organization_id=user.organization_id,
        user_id=user.id,
        action="user_login",
        resource_type="user",
        resource_id=str(user.id),
        ip_address=client_ip,
        user_agent=user_agent,
    )

    return TokenResponse(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
):
    return current_user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user_in: UserCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )

    user = create_user(db, current_user.organization_id, user_in)
    log_action(
        db,
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action="user_created",
        resource_type="user",
        resource_id=str(user.id),
        details={"email": user.email, "role": user.role},
    )
    return user
