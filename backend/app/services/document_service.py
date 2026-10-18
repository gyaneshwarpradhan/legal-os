"""Document processing pipeline service orchestrating custody, extraction, classification, chunking, and indexing."""
from pathlib import Path
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.document_version import DocumentVersion
from app.services.chunking import chunker
from app.services.classifier import classify_document
from app.services.embeddings import embedding_provider
from app.services.extraction import extractor
from app.services.storage import storage_service, validate_file_metadata


def process_uploaded_document(
    db: Session,
    matter_id: UUID,
    uploaded_by_id: UUID,
    file_name: str,
    file_bytes: bytes,
    document_type_override: Optional[str] = None,
) -> Document:
    """
    End-to-end document intelligence pipeline:
    1. Validation
    2. Secure storage custody
    3. Multi-format text extraction & OCR
    4. Classification & title extraction
    5. Page-aware chunking
    6. Embedding vector generation
    7. Storage in Matter Knowledge Base
    """
    file_size = len(file_bytes)
    validate_file_metadata(file_name, file_size)

    document_id = uuid4()
    storage_key = storage_service.save_file(
        matter_id=matter_id,
        document_id=document_id,
        file_name=file_name,
        content=file_bytes,
    )

    # 1. Create Document record
    doc = Document(
        id=document_id,
        matter_id=matter_id,
        title=Path(file_name).stem.replace("_", " ").title(),
        document_type=document_type_override or "other",
        file_name=file_name,
        file_type=Path(file_name).suffix.lower(),
        file_size=file_size,
        storage_key=storage_key,
        status="processing",
        uploaded_by_id=uploaded_by_id,
    )
    db.add(doc)
    db.flush()

    # 2. Create initial Version
    version = DocumentVersion(
        document_id=doc.id,
        version_number=1,
        file_name=file_name,
        storage_key=storage_key,
        file_size=file_size,
        uploaded_by_id=uploaded_by_id,
    )
    db.add(version)

    # 3. Extract text
    extracted = extractor.extract(file_name, file_bytes)

    # 4. Classify document
    predicted_type, confidence, candidate_title = classify_document(
        file_name, extracted.full_text
    )
    if not document_type_override:
        doc.document_type = predicted_type
        if candidate_title:
            doc.title = candidate_title

    # 5. Chunk text
    chunk_data_list = chunker.chunk_document(
        document_id=doc.id,
        matter_id=matter_id,
        extracted=extracted,
    )

    # 6. Embed chunks
    if chunk_data_list:
        chunk_texts = [c.content for c in chunk_data_list]
        embeddings = embedding_provider.embed_batch(chunk_texts)

        # 7. Persist chunks with denormalized matter_id
        for chunk_data, vec in zip(chunk_data_list, embeddings):
            chunk_metadata = chunk_data.metadata.copy()
            chunk_metadata["embedding"] = vec
            db_chunk = DocumentChunk(
                document_id=doc.id,
                matter_id=matter_id,
                chunk_index=chunk_data.chunk_index,
                content=chunk_data.content,
                page_number=chunk_data.page_number,
                token_count=chunk_data.token_count,
                metadata_=chunk_metadata,
            )
            db.add(db_chunk)

    # Mark document ready
    doc.status = "ready"
    doc.processing_status = {
        "pages_processed": extracted.total_pages,
        "chunks_generated": len(chunk_data_list),
        "classification_confidence": confidence,
        "predicted_type": predicted_type,
    }
    db.commit()
    db.refresh(doc)
    return doc


def get_matter_documents(db: Session, matter_id: UUID) -> List[Document]:
    return (
        db.query(Document)
        .filter(Document.matter_id == matter_id, Document.is_deleted == False)
        .order_by(Document.created_at.desc())
        .all()
    )


def get_document(db: Session, document_id: UUID, matter_id: UUID) -> Optional[Document]:
    return (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.matter_id == matter_id,
            Document.is_deleted == False,
        )
        .first()
    )


def get_document_chunks(
    db: Session, document_id: UUID, matter_id: UUID
) -> List[DocumentChunk]:
    return (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.document_id == document_id,
            DocumentChunk.matter_id == matter_id,
        )
        .order_by(DocumentChunk.chunk_index.asc())
        .all()
    )


def reclassify_document(
    db: Session, document_id: UUID, matter_id: UUID, new_type: str
) -> Document:
    doc = get_document(db, document_id, matter_id)
    if doc:
        doc.document_type = new_type
        db.commit()
        db.refresh(doc)
    return doc
