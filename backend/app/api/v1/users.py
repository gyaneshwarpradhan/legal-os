from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_active_user,
    get_db,
    require_role,
)
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.audit_service import log_action

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=List[UserResponse])
def list_users(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    users = (
        db.query(User)
        .filter(User.organization_id == current_user.organization_id)
        .order_by(User.full_name.asc())
        .all()
    )
    return users


@router.get("/{user_id}", response_model=UserResponse)
def get_user_detail(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.organization_id == current_user.organization_id,
        )
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    user_in: UserUpdate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.organization_id == current_user.organization_id,
        )
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    update_data = user_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    log_action(
        db,
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action="user_updated",
        resource_type="user",
        resource_id=str(user.id),
        details=update_data,
    )
    return user
