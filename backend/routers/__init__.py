from backend.routers.auth import router as auth_router
from backend.routers.samples import router as samples_router
from backend.routers.assessment import router as assessment_router
from backend.routers.dashboard import router as dashboard_router
from backend.routers.admin import router as admin_router

__all__ = [
    "auth_router",
    "samples_router",
    "assessment_router",
    "dashboard_router",
    "admin_router",
]
