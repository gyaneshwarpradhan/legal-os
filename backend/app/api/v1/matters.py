from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_active_user,
    get_db,
    require_matter_access,
    require_role,
)
from app.models.matter import Matter
from app.models.task import Task
from app.models.user import User
from app.schemas.matter import (
    ClaimCreate,
    ClaimResponse,
    DeadlineCreate,
    DeadlineResponse,
    EventCreate,
    EventResponse,
    ExpertCreate,
    ExpertResponse,
    MatterCreate,
    MatterListResponse,
    MatterMemberAdd,
    MatterMemberResponse,
    MatterResponse,
    MatterUpdate,
    PartyCreate,
    PartyResponse,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    WitnessCreate,
    WitnessResponse,
)
from app.schemas.user import UserBrief
from app.services import matter_service
from app.services.audit_service import log_action

router = APIRouter(prefix="/matters", tags=["matters"])


@router.get("", response_model=dict)
def list_matters(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * page_size
    matters, total = matter_service.get_user_matters(
        db=db,
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        user_role=current_user.role,
        skip=skip,
        limit=page_size,
        status_filter=status,
        search=search,
    )

    items = []
    for m in matters:
        member_count = matter_service.get_matter_member_count(db, m.id)
        items.append(
            MatterListResponse(
                id=m.id,
                title=m.title,
                case_number=m.case_number,
                matter_type=m.matter_type,
                status=m.status,
                date_opened=m.date_opened,
                member_count=member_count,
                created_at=m.created_at,
            )
        )

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("", response_model=MatterResponse, status_code=status.HTTP_201_CREATED)
def create_new_matter(
    matter_in: MatterCreate,
    current_user: User = Depends(require_role("admin", "managing_attorney", "attorney")),
    db: Session = Depends(get_db),
):
    matter = matter_service.create_matter(
        db=db,
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        data=matter_in,
    )
    log_action(
        db,
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action="matter_created",
        matter_id=matter.id,
        resource_type="matter",
        resource_id=str(matter.id),
        details={"title": matter.title, "case_number": matter.case_number},
    )
    member_count = matter_service.get_matter_member_count(db, matter.id)
    return MatterResponse(
        id=matter.id,
        organization_id=matter.organization_id,
        title=matter.title,
        case_number=matter.case_number,
        description=matter.description,
        matter_type=matter.matter_type,
        status=matter.status,
        date_opened=matter.date_opened,
        date_closed=matter.date_closed,
        court=matter.court,
        jurisdiction=matter.jurisdiction,
        judge=matter.judge,
        created_by=UserBrief.model_validate(current_user),
        member_count=member_count,
        created_at=matter.created_at,
        updated_at=matter.updated_at,
    )


@router.get("/{matter_id}", response_model=MatterResponse)
def get_matter_detail(
    matter_id: UUID,
    matter: Matter = Depends(require_matter_access),
    db: Session = Depends(get_db),
):
    member_count = matter_service.get_matter_member_count(db, matter.id)
    return MatterResponse(
        id=matter.id,
        organization_id=matter.organization_id,
        title=matter.title,
        case_number=matter.case_number,
        description=matter.description,
        matter_type=matter.matter_type,
        status=matter.status,
        date_opened=matter.date_opened,
        date_closed=matter.date_closed,
        court=matter.court,
        jurisdiction=matter.jurisdiction,
        judge=matter.judge,
        created_by=UserBrief.model_validate(matter.created_by) if matter.created_by else None,
        member_count=member_count,
        created_at=matter.created_at,
        updated_at=matter.updated_at,
    )


@router.put("/{matter_id}", response_model=MatterResponse)
def update_matter_detail(
    matter_id: UUID,
    matter_in: MatterUpdate,
    matter: Matter = Depends(require_matter_access),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    updated = matter_service.update_matter(db, matter, matter_in)
    log_action(
        db,
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action="matter_updated",
        matter_id=matter.id,
        resource_type="matter",
        resource_id=str(matter.id),
    )
    member_count = matter_service.get_matter_member_count(db, updated.id)
    return MatterResponse(
        id=updated.id,
        organization_id=updated.organization_id,
        title=updated.title,
        case_number=updated.case_number,
        description=updated.description,
        matter_type=updated.matter_type,
        status=updated.status,
        date_opened=updated.date_opened,
        date_closed=updated.date_closed,
        court=updated.court,
        jurisdiction=updated.jurisdiction,
        judge=updated.judge,
        created_by=UserBrief.model_validate(updated.created_by) if updated.created_by else None,
        member_count=member_count,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
    )


# ---------- Members ----------


@router.get("/{matter_id}/members", response_model=List[MatterMemberResponse])
def get_matter_members(
    matter_id: UUID,
    matter: Matter = Depends(require_matter_access),
    db: Session = Depends(get_db),
):
    members = matter_service.get_matter_members(db, matter.id)
    return [
        MatterMemberResponse(
            id=m.id,
            user=UserBrief.model_validate(m.user),
            role=m.role,
            created_at=m.created_at,
        )
        for m in members
    ]


@router.post("/{matter_id}/members", response_model=MatterMemberResponse)
def add_matter_member(
    matter_id: UUID,
    member_in: MatterMemberAdd,
    matter: Matter = Depends(require_matter_access),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    member = matter_service.add_matter_member(
        db, matter.id, member_in, added_by_id=current_user.id
    )
    log_action(
        db,
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action="matter_member_added",
        matter_id=matter.id,
        resource_type="matter_member",
        resource_id=str(member.id),
        details={"user_id": str(member_in.user_id), "role": member_in.role},
    )
    return MatterMemberResponse(
        id=member.id,
        user=UserBrief.model_validate(member.user),
        role=member.role,
        created_at=member.created_at,
    )


@router.delete("/{matter_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_matter_member(
    matter_id: UUID,
    user_id: UUID,
    matter: Matter = Depends(require_matter_access),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    removed = matter_service.remove_matter_member(db, matter.id, user_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in this matter",
        )
    log_action(
        db,
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action="matter_member_removed",
        matter_id=matter.id,
        details={"user_id": str(user_id)},
    )


# ---------- Parties ----------


@router.get("/{matter_id}/parties", response_model=List[PartyResponse])
def get_parties(
    matter_id: UUID,
    matter: Matter = Depends(require_matter_access),
    db: Session = Depends(get_db),
):
    return matter_service.get_parties(db, matter.id)


@router.post("/{matter_id}/parties", response_model=PartyResponse, status_code=status.HTTP_201_CREATED)
def add_party(
    matter_id: UUID,
    party_in: PartyCreate,
    matter: Matter = Depends(require_matter_access),
    db: Session = Depends(get_db),
):
    return matter_service.create_party(db, matter.id, party_in)


# ---------- Witnesses ----------


@router.get("/{matter_id}/witnesses", response_model=List[WitnessResponse])
def get_witnesses(
    matter_id: UUID,
    matter: Matter = Depends(require_matter_access),
    db: Session = Depends(get_db),
):
    return matter_service.get_witnesses(db, matter.id)


@router.post("/{matter_id}/witnesses", response_model=WitnessResponse, status_code=status.HTTP_201_CREATED)
def add_witness(
    matter_id: UUID,
    witness_in: WitnessCreate,
    matter: Matter = Depends(require_matter_access),
    db: Session = Depends(get_db),
):
    return matter_service.create_witness(db, matter.id, witness_in)


# ---------- Experts ----------


@router.get("/{matter_id}/experts", response_model=List[ExpertResponse])
def get_experts(
    matter_id: UUID,
    matter: Matter = Depends(require_matter_access),
    db: Session = Depends(get_db),
):
    return matter_service.get_experts(db, matter.id)


@router.post("/{matter_id}/experts", response_model=ExpertResponse, status_code=status.HTTP_201_CREATED)
def add_expert(
    matter_id: UUID,
    expert_in: ExpertCreate,
    matter: Matter = Depends(require_matter_access),
    db: Session = Depends(get_db),
):
    return matter_service.create_expert(db, matter.id, expert_in)


# ---------- Claims ----------


@router.get("/{matter_id}/claims", response_model=List[ClaimResponse])
def get_claims(
    matter_id: UUID,
    matter: Matter = Depends(require_matter_access),
    db: Session = Depends(get_db),
):
    return matter_service.get_claims(db, matter.id)


@router.post("/{matter_id}/claims", response_model=ClaimResponse, status_code=status.HTTP_201_CREATED)
def add_claim(
    matter_id: UUID,
    claim_in: ClaimCreate,
    matter: Matter = Depends(require_matter_access),
    db: Session = Depends(get_db),
):
    return matter_service.create_claim(db, matter.id, claim_in)


# ---------- Events (Timeline) ----------


@router.get("/{matter_id}/events", response_model=List[EventResponse])
def get_events(
    matter_id: UUID,
    matter: Matter = Depends(require_matter_access),
    db: Session = Depends(get_db),
):
    return matter_service.get_events(db, matter.id)


@router.post("/{matter_id}/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def add_event(
    matter_id: UUID,
    event_in: EventCreate,
    matter: Matter = Depends(require_matter_access),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return matter_service.create_event(db, matter.id, event_in, created_by_id=current_user.id)


# ---------- Deadlines ----------


@router.get("/{matter_id}/deadlines", response_model=List[DeadlineResponse])
def get_deadlines(
    matter_id: UUID,
    matter: Matter = Depends(require_matter_access),
    db: Session = Depends(get_db),
):
    return matter_service.get_deadlines(db, matter.id)


@router.post("/{matter_id}/deadlines", response_model=DeadlineResponse, status_code=status.HTTP_201_CREATED)
def add_deadline(
    matter_id: UUID,
    deadline_in: DeadlineCreate,
    matter: Matter = Depends(require_matter_access),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return matter_service.create_deadline(db, matter.id, deadline_in, created_by_id=current_user.id)


# ---------- Tasks ----------


@router.get("/{matter_id}/tasks", response_model=List[TaskResponse])
def get_tasks(
    matter_id: UUID,
    matter: Matter = Depends(require_matter_access),
    db: Session = Depends(get_db),
):
    return matter_service.get_tasks(db, matter.id)


@router.post("/{matter_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def add_task(
    matter_id: UUID,
    task_in: TaskCreate,
    matter: Matter = Depends(require_matter_access),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return matter_service.create_task(db, matter.id, task_in, created_by_id=current_user.id)


@router.put("/{matter_id}/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    matter_id: UUID,
    task_id: UUID,
    task_in: TaskUpdate,
    matter: Matter = Depends(require_matter_access),
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id, Task.matter_id == matter.id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return matter_service.update_task(db, task, task_in)
