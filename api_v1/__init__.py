from fastapi import APIRouter

from .files.views import router as files_router
from .auth.views import router as demo_auth_router

router = APIRouter()
router.include_router(router=files_router, prefix="/files")
router.include_router(router=demo_auth_router)
