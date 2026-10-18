"""
API Dependencies — CRITICAL SECURITY MODULE

This module contains the authentication and authorization dependencies
that protect every API endpoint. Matter isolation is enforced here.
"""
from typing import Generator
from uuid import UUID

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal, get_db
from app.core.exceptions import (
    AuthenticationError,
    MatterAccessDeniedError,
    NotFoundError,
    PermissionDeniedError,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """Decode JWT and return the authenticated user. Raises 401 on failure."""
    from app.models.user import User

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise AuthenticationError()
    except JWTError:
        raise AuthenticationError()

    try:
        user_uuid = UUID(user_id)
    except (ValueError, TypeError):
        raise AuthenticationError()

    user = db.query(User).filter(User.id == user_uuid).first()
    if user is None:
        raise AuthenticationError()
    if not user.is_active:
        raise AuthenticationError(detail="User account is deactivated")
    return user


async def get_current_active_user(
    current_user=Depends(get_current_user),
):
    """Verify the user is active. Convenience wrapper."""
    if not current_user.is_active:
        raise PermissionDeniedError(detail="Inactive user")
    return current_user


def require_role(*roles: str):
    """
    Returns a dependency that checks the current user has one of the
    specified roles. Usage:

        @router.get("/admin", dependencies=[Depends(require_role("admin"))])
    """

    async def role_checker(
        current_user=Depends(get_current_active_user),
    ):
        user_role = current_user.role
        if hasattr(user_role, "value"):
            user_role = user_role.value
        if user_role not in roles:
            raise PermissionDeniedError(
                detail=f"Role '{user_role}' is not authorized for this action"
            )
        return current_user

    return role_checker


async def require_matter_access(
    matter_id: UUID,
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    CORE MATTER ISOLATION GATE.

    1. Look up matter by ID within user's organization.
    2. Check user is a member of the matter OR is an admin.
    3. Raise MatterAccessDeniedError if unauthorized.
    4. Return the matter object.

    Authorization happens BEFORE any data retrieval.
    """
    from app.models.matter import Matter
    from app.models.matter_member import MatterMember

    matter = (
        db.query(Matter)
        .filter(
            Matter.id == matter_id,
            Matter.organization_id == current_user.organization_id,
            Matter.is_deleted == False,
        )
        .first()
    )

    if matter is None:
        raise NotFoundError(detail="Matter not found")

    # Admins have access to all matters in their organization
    user_role = current_user.role
    if hasattr(user_role, "value"):
        user_role = user_role.value
    if user_role == "admin":
        return matter

    # Check matter membership
    membership = (
        db.query(MatterMember)
        .filter(
            MatterMember.matter_id == matter_id,
            MatterMember.user_id == current_user.id,
        )
        .first()
    )

    if membership is None:
        raise MatterAccessDeniedError()

    return matter


def get_client_ip(request: Request) -> str | None:
    """Extract client IP from the request for audit logging."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None
