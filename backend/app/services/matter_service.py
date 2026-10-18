"""Matter service — CRUD operations for matters and all matter entities."""
from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.claim import Claim
from app.models.deadline import Deadline
from app.models.event import Event
from app.models.expert import Expert
from app.models.matter import Matter
from app.models.matter_member import MatterMember
from app.models.party import Party
from app.models.task import Task
from app.models.witness import Witness
from app.schemas.matter import (
    ClaimCreate,
    DeadlineCreate,
    EventCreate,
    ExpertCreate,
    MatterCreate,
    MatterMemberAdd,
    MatterUpdate,
    PartyCreate,
    TaskCreate,
    TaskUpdate,
    WitnessCreate,
)


# ---------- Matter CRUD ----------


def create_matter(
    db: Session,
    organization_id: UUID,
    user_id: UUID,
    data: MatterCreate,
) -> Matter:
    matter = Matter(
        organization_id=organization_id,
        title=data.title,
        case_number=data.case_number,
        description=data.description,
        matter_type=data.matter_type,
        status="active",
        date_opened=data.date_opened,
        court=data.court,
        jurisdiction=data.jurisdiction,
        judge=data.judge,
        created_by_id=user_id,
    )
    db.add(matter)
    db.flush()

    # Creator becomes lead attorney on the matter
    member = MatterMember(
        matter_id=matter.id,
        user_id=user_id,
        role="lead_attorney",
        added_by_id=user_id,
    )
    db.add(member)
    db.commit()
    db.refresh(matter)
    return matter


def get_user_matters(
    db: Session,
    user_id: UUID,
    organization_id: UUID,
    user_role: str,
    skip: int = 0,
    limit: int = 25,
    status_filter: Optional[str] = None,
    search: Optional[str] = None,
) -> Tuple[List[Matter], int]:
    """Return matters the user is authorized to see."""
    query = db.query(Matter).filter(
        Matter.organization_id == organization_id,
        Matter.is_deleted == False,
    )

    # Non-admin users only see matters they are members of
    if user_role != "admin":
        query = query.join(MatterMember).filter(
            MatterMember.user_id == user_id,
        )

    if status_filter and status_filter != "all":
        query = query.filter(Matter.status == status_filter)

    if search:
        query = query.filter(
            or_(
                Matter.title.ilike(f"%{search}%"),
                Matter.case_number.ilike(f"%{search}%"),
            )
        )

    total = query.count()
    matters = query.order_by(Matter.created_at.desc()).offset(skip).limit(limit).all()
    return matters, total


def get_matter(db: Session, matter_id: UUID) -> Matter | None:
    return db.query(Matter).filter(Matter.id == matter_id).first()


def update_matter(
    db: Session,
    matter: Matter,
    data: MatterUpdate,
) -> Matter:
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(matter, key, value)
    db.commit()
    db.refresh(matter)
    return matter


def get_matter_member_count(db: Session, matter_id: UUID) -> int:
    return db.query(func.count(MatterMember.id)).filter(
        MatterMember.matter_id == matter_id
    ).scalar() or 0


# ---------- Matter Members ----------


def add_matter_member(
    db: Session,
    matter_id: UUID,
    data: MatterMemberAdd,
    added_by_id: UUID,
) -> MatterMember:
    member = MatterMember(
        matter_id=matter_id,
        user_id=data.user_id,
        role=data.role,
        added_by_id=added_by_id,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def get_matter_members(db: Session, matter_id: UUID) -> List[MatterMember]:
    return (
        db.query(MatterMember)
        .options(joinedload(MatterMember.user))
        .filter(MatterMember.matter_id == matter_id)
        .all()
    )


def remove_matter_member(db: Session, matter_id: UUID, user_id: UUID) -> bool:
    member = (
        db.query(MatterMember)
        .filter(
            MatterMember.matter_id == matter_id,
            MatterMember.user_id == user_id,
        )
        .first()
    )
    if member:
        db.delete(member)
        db.commit()
        return True
    return False


# ---------- Parties ----------

def create_party(db: Session, matter_id: UUID, data: PartyCreate) -> Party:
    party = Party(matter_id=matter_id, **data.model_dump())
    db.add(party)
    db.commit()
    db.refresh(party)
    return party


def get_parties(db: Session, matter_id: UUID) -> List[Party]:
    return db.query(Party).filter(Party.matter_id == matter_id).all()


# ---------- Witnesses ----------

def create_witness(db: Session, matter_id: UUID, data: WitnessCreate) -> Witness:
    witness = Witness(matter_id=matter_id, **data.model_dump())
    db.add(witness)
    db.commit()
    db.refresh(witness)
    return witness


def get_witnesses(db: Session, matter_id: UUID) -> List[Witness]:
    return db.query(Witness).filter(Witness.matter_id == matter_id).all()


# ---------- Experts ----------

def create_expert(db: Session, matter_id: UUID, data: ExpertCreate) -> Expert:
    expert = Expert(matter_id=matter_id, **data.model_dump())
    db.add(expert)
    db.commit()
    db.refresh(expert)
    return expert


def get_experts(db: Session, matter_id: UUID) -> List[Expert]:
    return db.query(Expert).filter(Expert.matter_id == matter_id).all()


# ---------- Claims ----------

def create_claim(db: Session, matter_id: UUID, data: ClaimCreate) -> Claim:
    claim = Claim(matter_id=matter_id, **data.model_dump())
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim


def get_claims(db: Session, matter_id: UUID) -> List[Claim]:
    return db.query(Claim).filter(Claim.matter_id == matter_id).all()


# ---------- Events (Timeline) ----------

def create_event(
    db: Session, matter_id: UUID, data: EventCreate, created_by_id: UUID
) -> Event:
    event = Event(
        matter_id=matter_id,
        created_by_id=created_by_id,
        **data.model_dump(),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_events(db: Session, matter_id: UUID) -> List[Event]:
    return (
        db.query(Event)
        .filter(Event.matter_id == matter_id)
        .order_by(Event.event_date.asc())
        .all()
    )


# ---------- Deadlines ----------

def create_deadline(
    db: Session, matter_id: UUID, data: DeadlineCreate, created_by_id: UUID
) -> Deadline:
    deadline = Deadline(
        matter_id=matter_id,
        created_by_id=created_by_id,
        status="pending",
        **data.model_dump(),
    )
    db.add(deadline)
    db.commit()
    db.refresh(deadline)
    return deadline


def get_deadlines(db: Session, matter_id: UUID) -> List[Deadline]:
    return (
        db.query(Deadline)
        .filter(Deadline.matter_id == matter_id)
        .order_by(Deadline.due_date.asc())
        .all()
    )


# ---------- Tasks ----------

def create_task(
    db: Session, matter_id: UUID, data: TaskCreate, created_by_id: UUID
) -> Task:
    task = Task(
        matter_id=matter_id,
        created_by_id=created_by_id,
        status="todo",
        **data.model_dump(),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_tasks(db: Session, matter_id: UUID) -> List[Task]:
    return (
        db.query(Task)
        .filter(Task.matter_id == matter_id)
        .order_by(Task.created_at.desc())
        .all()
    )


def update_task(db: Session, task: Task, data: TaskUpdate) -> Task:
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    if data.status == "completed":
        task.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    return task
