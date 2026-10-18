"""Page-aware recursive chunking engine preserving citations and matter context."""
from dataclasses import dataclass
from typing import Dict, List, Optional
from uuid import UUID

from app.services.extraction import ExtractedDocument


@dataclass
class DocumentChunkData:
    chunk_index: int
    content: str
    page_number: Optional[int]
    token_count: int
    metadata: Dict[str, any]


class LegalChunker:
    def __init__(self, target_chunk_size: int = 1000, overlap_size: int = 150):
        self.target_chunk_size = target_chunk_size
        self.overlap_size = overlap_size

    def chunk_document(
        self,
        document_id: UUID,
        matter_id: UUID,
        extracted: ExtractedDocument,
    ) -> List[DocumentChunkData]:
        chunks: List[DocumentChunkData] = []
        global_index = 0

        for page in extracted.pages:
            page_text = page.text.strip()
            if not page_text:
                continue

            page_chunks = self._chunk_page_text(
                page_text=page_text,
                page_number=page.page_number,
                document_id=document_id,
                matter_id=matter_id,
                start_index=global_index,
            )
            chunks.extend(page_chunks)
            global_index += len(page_chunks)

        # Fallback if no pages produced chunks
        if not chunks and extracted.full_text.strip():
            fallback_chunks = self._chunk_page_text(
                page_text=extracted.full_text.strip(),
                page_number=1,
                document_id=document_id,
                matter_id=matter_id,
                start_index=0,
            )
            chunks.extend(fallback_chunks)

        return chunks

    def _chunk_page_text(
        self,
        page_text: str,
        page_number: int,
        document_id: UUID,
        matter_id: UUID,
        start_index: int,
    ) -> List[DocumentChunkData]:
        chunks = []
        text_len = len(page_text)
        current_pos = 0
        current_index = start_index

        while current_pos < text_len:
            end_pos = min(current_pos + self.target_chunk_size, text_len)

            # Try to break on a sentence or paragraph boundary
            if end_pos < text_len:
                break_point = max(
                    page_text.rfind("\n\n", current_pos, end_pos),
                    page_text.rfind(". ", current_pos, end_pos),
                )
                if break_point > current_pos + (self.target_chunk_size // 2):
                    end_pos = break_point + 1

            chunk_content = page_text[current_pos:end_pos].strip()
            if chunk_content:
                approx_tokens = max(1, int(len(chunk_content.split()) * 1.3))
                chunks.append(
                    DocumentChunkData(
                        chunk_index=current_index,
                        content=chunk_content,
                        page_number=page_number,
                        token_count=approx_tokens,
                        metadata={
                            "document_id": str(document_id),
                            "matter_id": str(matter_id),
                            "page": page_number,
                            "char_start": current_pos,
                            "char_end": end_pos,
                        },
                    )
                )
                current_index += 1

            # Advance with overlap
            current_pos = end_pos - self.overlap_size
            if current_pos >= text_len - self.overlap_size or end_pos >= text_len:
                break

        return chunks


chunker = LegalChunker()
