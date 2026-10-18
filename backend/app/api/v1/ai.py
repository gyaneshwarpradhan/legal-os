from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from app.api.deps import get_db, require_matter_access, get_current_active_user
from app.models.matter import Matter
from app.models.user import User
from app.schemas.ai import (
    AIAskRequest,
    AIAskResponse,
    AISummarizeRequest,
    AISummarizeResponse,
    AITimelineRequest,
    AITimelineResponse,
)
from app.ai.workflows.qa import answer_question
from app.ai.workflows.summarization import summarize_document
from app.ai.workflows.timeline import extract_timeline
from sqlalchemy.orm import Session

router = APIRouter(prefix="/matters/{matter_id}", tags=["ai"])

@router.post("/ai/ask", response_model=AIAskResponse)
async def ask_ai(
    matter_id: UUID,
    payload: AIAskRequest,
    matter: Matter = Depends(require_matter_access),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Answer a user question using the AI workflow.

    Returns the answer text and a list of citation objects.
    """
    if matter.id != matter_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Matter ID mismatch")
    answer, citations = await answer_question(
        db=db,
        matter_id=str(matter_id),
        question=payload.question,
        user_id=str(current_user.id),
    )
    return AIAskResponse(answer=answer, citations=citations)

@router.post("/ai/summarize-document/{document_id}", response_model=AISummarizeResponse)
async def summarize_ai(
    matter_id: UUID,
    document_id: UUID,
    payload: AISummarizeRequest,
    matter: Matter = Depends(require_matter_access),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Generate a summary for a document with citations."""
    if matter.id != matter_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Matter ID mismatch")
    summary, citations = await summarize_document(
        db=db,
        matter_id=str(matter_id),
        document_id=str(document_id),
        user_id=str(current_user.id),
    )
    return AISummarizeResponse(summary=summary, citations=citations)

@router.post("/ai/extract-timeline", response_model=AITimelineResponse)
async def timeline_ai(
    matter_id: UUID,
    payload: AITimelineRequest,
    matter: Matter = Depends(require_matter_access),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Extract a timeline based on a free‑form query.

    Returns a list of timeline events with optional citations.
    """
    if matter.id != matter_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Matter ID mismatch")
    timeline, citations = await extract_timeline(
        db=db,
        matter_id=str(matter_id),
        query=payload.query,
        user_id=str(current_user.id),
    )
    return AITimelineResponse(timeline=timeline, citations=citations)
