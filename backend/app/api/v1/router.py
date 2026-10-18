from fastapi import APIRouter

from app.api.v1.audit import router as audit_router
from app.api.v1.auth import router as auth_router
from app.api.v1.documents import router as documents_router
from app.api.v1.matters import router as matters_router
from app.api.v1.users import router as users_router

api_router = APIRouter()
from app.api.v1.ai import router as ai_router
api_router.include_router(auth_router)
api_router.include_router(matters_router)
api_router.include_router(documents_router)
api_router.include_router(users_router)
api_router.include_router(ai_router)
