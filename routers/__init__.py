"""
API Routers for FT9 Intelligence
"""
from routers.auth_router import router as auth_router
from routers.organization_router import router as organization_router
from routers.billing_router import router as billing_router
from routers.knowledge_router import router as knowledge_router
from routers.automation_router import router as automation_router

__all__ = [
    "auth_router",
    "organization_router",
    "billing_router",
    "knowledge_router",
    "automation_router"
]
