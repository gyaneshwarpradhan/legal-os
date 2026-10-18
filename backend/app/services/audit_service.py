"""Audit service — append-only audit trail for security-sensitive events."""
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def log_action(
    db: Session,
    *,
    organization_id: UUID,
    user_id: Optional[UUID] = None,
    action: str,
    matter_id: Optional[UUID] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> AuditLog:
    """
    Create an audit log entry. Audit logs are append-only and
    should never be updated or deleted.
    """
    entry = AuditLog(
        organization_id=organization_id,
        user_id=user_id,
        action=action,
        matter_id=matter_id,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
