from typing import List, Optional
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_active_user,
    get_db,
    require_matter_access,
)
from app.models.matter import Matter
from app.models.user import User
from app.schemas.document import (
    DocumentChunkResponse,
    DocumentResponse,
    ReclassifyRequest,
    SearchRequest,
    SearchResultResponse,
)
from app.services import document_service, search
from app.services.audit_service import log_action

router = APIRouter(prefix="/matters/{matter_id}", tags=["documents"])


@router.post(
    "/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    matter_id: UUID,
    file: UploadFile = File(...),
    document_type: Optional[str] = Form(None),
    matter: Matter = Depends(require_matter_access),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Upload and immediately process a confidential matter document.
    Executes extraction, classification, chunking, and vector indexing.
    """
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    try:
        doc = document_service.process_uploaded_document(
            db=db,
            matter_id=matter.id,
            uploaded_by_id=current_user.id,
            file_name=file.filename or "unnamed_document",
            file_bytes=file_bytes,
            document_type_override=document_type,
        )

        log_action(
            db,
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            action="document_uploaded",
            matter_id=matter.id,
            resource_type="document",
            resource_id=str(doc.id),
            details={
                "file_name": doc.file_name,
                "classified_type": doc.document_type,
                "size_bytes": doc.file_size,
            },
        )
        return doc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Document processing failed: {str(e)}",
        )


@router.get("/documents", response_model=List[DocumentResponse])
def list_documents(
    matter_id: UUID,
    matter: Matter = Depends(require_matter_access),
    db: Session = Depends(get_db),
):
    """List all authorized documents within this matter."""
    return document_service.get_matter_documents(db, matter.id)


@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document_detail(
    matter_id: UUID,
    document_id: UUID,
    matter: Matter = Depends(require_matter_access),
    db: Session = Depends(get_db),
):
    doc = document_service.get_document(db, document_id, matter.id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found in this matter.",
        )
    return doc


@router.get(
    "/documents/{document_id}/chunks",
    response_model=List[DocumentChunkResponse],
)
def get_document_chunks(
    matter_id: UUID,
    document_id: UUID,
    matter: Matter = Depends(require_matter_access),
    db: Session = Depends(get_db),
):
    """Inspect chunk-level segmentation and page numbers for citation inspection."""
    return document_service.get_document_chunks(db, document_id, matter.id)


@router.put(
    "/documents/{document_id}/reclassify",
    response_model=DocumentResponse,
)
def reclassify_document(
    matter_id: UUID,
    document_id: UUID,
    payload: ReclassifyRequest,
    matter: Matter = Depends(require_matter_access),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Attorney override of AI document classification."""
    doc = document_service.reclassify_document(
        db, document_id, matter.id, payload.document_type
    )
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found in this matter.",
        )

    log_action(
        db,
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action="document_reclassified",
        matter_id=matter.id,
        resource_type="document",
        resource_id=str(doc.id),
        details={"new_type": payload.document_type},
    )
    return doc


@router.post("/search", response_model=List[SearchResultResponse])
def search_matter(
    matter_id: UUID,
    payload: SearchRequest,
    matter: Matter = Depends(require_matter_access),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Search across all documents and chunks strictly within this matter.
    Combines semantic embeddings and keyword hits with hard matter-boundary isolation.
    """
    results = search.search_matter_knowledge(
        db=db,
        matter_id=matter.id,
        query=payload.query,
        limit=payload.limit or 10,
    )

    log_action(
        db,
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action="matter_searched",
        matter_id=matter.id,
        details={"query_length": len(payload.query), "results_count": len(results)},
    )

    return [
        SearchResultResponse(
            chunk_id=r.chunk_id,
            document_id=r.document_id,
            document_title=r.document_title,
            page_number=r.page_number,
            content=r.content,
            score=r.score,
            match_type=r.match_type,
        )
        for r in results
    ]
