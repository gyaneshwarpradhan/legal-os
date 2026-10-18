from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.user import UserBrief


# ---------- Matter ----------

class MatterCreate(BaseModel):
    title: str
    case_number: Optional[str] = None
    description: Optional[str] = None
    matter_type: str = "other"
    date_opened: date
    court: Optional[str] = None
    jurisdiction: Optional[str] = None
    judge: Optional[str] = None


class MatterUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    case_number: Optional[str] = None
    court: Optional[str] = None
    jurisdiction: Optional[str] = None
    judge: Optional[str] = None
    date_closed: Optional[date] = None


class MatterListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    case_number: Optional[str] = None
    matter_type: str
    status: str
    date_opened: date
    member_count: int = 0
    created_at: datetime


class MatterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    title: str
    case_number: Optional[str] = None
    description: Optional[str] = None
    matter_type: str
    status: str
    date_opened: date
    date_closed: Optional[date] = None
    court: Optional[str] = None
    jurisdiction: Optional[str] = None
    judge: Optional[str] = None
    created_by: Optional[UserBrief] = None
    member_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None


# ---------- Matter Member ----------

class MatterMemberAdd(BaseModel):
    user_id: UUID
    role: str = "attorney"


class MatterMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user: UserBrief
    role: str
    created_at: datetime


# ---------- Party ----------

class PartyCreate(BaseModel):
    name: str
    party_type: str = "plaintiff"
    entity_type: str = "individual"
    description: Optional[str] = None
    contact_info: Optional[Dict[str, Any]] = None


class PartyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    matter_id: UUID
    name: str
    party_type: str
    entity_type: str
    description: Optional[str] = None
    contact_info: Optional[Dict[str, Any]] = None
    created_at: datetime


# ---------- Witness ----------

class WitnessCreate(BaseModel):
    name: str
    witness_type: str = "fact"
    description: Optional[str] = None
    contact_info: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class WitnessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    matter_id: UUID
    name: str
    witness_type: str
    description: Optional[str] = None
    contact_info: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    created_at: datetime


# ---------- Expert ----------

class ExpertCreate(BaseModel):
    name: str
    specialty: str
    organization_name: Optional[str] = None
    contact_info: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    retained_by: str = "plaintiff"


class ExpertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    matter_id: UUID
    name: str
    specialty: str
    organization_name: Optional[str] = None
    notes: Optional[str] = None
    retained_by: str
    created_at: datetime


# ---------- Claim ----------

class ClaimCreate(BaseModel):
    title: str
    description: str
    claim_type: str
    status: str = "active"


class ClaimResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    matter_id: UUID
    title: str
    description: str
    claim_type: str
    status: str
    created_at: datetime


# ---------- Event (Timeline) ----------

class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    event_date: datetime
    event_type: str = "other"
    is_ai_generated: bool = False
    confidence: Optional[float] = None


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    matter_id: UUID
    title: str
    description: Optional[str] = None
    event_date: datetime
    event_type: str
    is_ai_generated: bool
    confidence: Optional[float] = None
    created_by_id: Optional[UUID] = None
    created_at: datetime


# ---------- Deadline ----------

class DeadlineCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: datetime
    deadline_type: str = "internal"
    is_high_risk: bool = False
    requires_review: bool = False
    assigned_to_id: Optional[UUID] = None


class DeadlineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    matter_id: UUID
    title: str
    description: Optional[str] = None
    due_date: datetime
    deadline_type: str
    status: str
    is_high_risk: bool
    requires_review: bool
    assigned_to_id: Optional[UUID] = None
    created_by_id: UUID
    created_at: datetime


# ---------- Task ----------

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    assigned_to_id: Optional[UUID] = None
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to_id: Optional[UUID] = None
    due_date: Optional[datetime] = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    matter_id: UUID
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    assigned_to_id: Optional[UUID] = None
    created_by_id: UUID
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
