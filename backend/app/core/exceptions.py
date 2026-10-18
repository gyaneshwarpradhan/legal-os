from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class LegalOSException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, str]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class NotFoundError(LegalOSException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class PermissionDeniedError(LegalOSException):
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class MatterAccessDeniedError(PermissionDeniedError):
    def __init__(
        self,
        detail: str = "Access denied: You are not authorized to view or modify this legal matter.",
    ):
        super().__init__(detail=detail)


class AuthenticationError(LegalOSException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ValidationError(LegalOSException):
    def __init__(self, detail: str = "Validation error"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail
        )
