from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import (
    get_db,
    require_role,
)
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit import AuditLogResponse

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=dict)
def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    matter_id: Optional[UUID] = Query(None),
    user_id: Optional[UUID] = Query(None),
    action: Optional[str] = Query(None),
    current_user: User = Depends(require_role("admin", "managing_attorney")),
    db: Session = Depends(get_db),
):
    query = db.query(AuditLog).filter(
        AuditLog.organization_id == current_user.organization_id
    )

    if matter_id:
        query = query.filter(AuditLog.matter_id == matter_id)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)

    total = query.count()
    logs = (
        query.order_by(AuditLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": [AuditLogResponse.model_validate(log) for log in logs],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
