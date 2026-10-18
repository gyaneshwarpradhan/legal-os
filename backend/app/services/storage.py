"""Storage service abstraction supporting local filesystem and S3/MinIO."""
import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
from uuid import UUID

from app.core.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".csv", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB


class StorageError(Exception):
    pass


class StorageValidationError(StorageError):
    pass


def validate_file_metadata(file_name: str, file_size: int):
    """Ensure file matches security constraints."""
    ext = Path(file_name).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise StorageValidationError(
            f"File extension '{ext}' is not permitted. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )
    if file_size > MAX_FILE_SIZE_BYTES:
        raise StorageValidationError(
            f"File size {file_size} bytes exceeds maximum limit of {MAX_FILE_SIZE_BYTES} bytes."
        )


class StorageService(ABC):
    @abstractmethod
    def save_file(
        self,
        matter_id: UUID,
        document_id: UUID,
        file_name: str,
        content: bytes,
    ) -> str:
        """Save file bytes and return a unique storage_key."""
        pass

    @abstractmethod
    def get_file_content(self, storage_key: str) -> bytes:
        """Retrieve file bytes given a storage_key."""
        pass

    @abstractmethod
    def get_download_url(self, storage_key: str, expires_in: int = 3600) -> str:
        """Return a URL or path for downloading the file."""
        pass


class LocalStorageService(StorageService):
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir or os.path.join(os.getcwd(), "storage", "matters"))
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_file(
        self,
        matter_id: UUID,
        document_id: UUID,
        file_name: str,
        content: bytes,
    ) -> str:
        validate_file_metadata(file_name, len(content))
        matter_dir = self.base_dir / str(matter_id)
        matter_dir.mkdir(parents=True, exist_ok=True)

        safe_name = f"{document_id}_{Path(file_name).name}"
        target_path = matter_dir / safe_name

        with open(target_path, "wb") as f:
            f.write(content)

        # Storage key is relative to base_dir for portability
        return f"{matter_id}/{safe_name}"

    def get_file_content(self, storage_key: str) -> bytes:
        file_path = self.base_dir / storage_key
        if not file_path.exists():
            raise StorageError(f"Storage key '{storage_key}' not found on disk.")
        with open(file_path, "rb") as f:
            return f.read()

    def get_download_url(self, storage_key: str, expires_in: int = 3600) -> str:
        # In local development, return API download endpoint
        return f"/api/v1/storage/download?key={storage_key}"


# Global instance
storage_service: StorageService = LocalStorageService()
