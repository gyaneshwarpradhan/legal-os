"""Authentication service — user verification and creation."""
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """Verify email + password and return user, or None on failure."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_user(
    db: Session,
    organization_id: UUID,
    user_data: UserCreate,
) -> User:
    """Create a new user with a hashed password."""
    user = User(
        organization_id=organization_id,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
