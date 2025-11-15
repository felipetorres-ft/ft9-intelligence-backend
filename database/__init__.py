"""
Database module for FT9 Intelligence
"""
from .database import (
    get_db,
    init_db,
    engine,
    AsyncSessionLocal,
)

# EXPORTAÇÃO NECESSÁRIA (PATCH AI9)
from .database import get_async_session

# Modelos e enums
from .models import (
    Base,
    Organization,
    User,
    Conversation,
    Message,
    KnowledgeBase,
    UserRole,
    SubscriptionPlan,
    SubscriptionStatus,
)

__all__ = [
    "get_db",
    "init_db",
    "engine",
    "AsyncSessionLocal",
    "get_async_session",  # essencial
    "Base",
    "Organization",
    "User",
    "Conversation",
    "Message",
    "KnowledgeBase",
    "UserRole",
    "SubscriptionPlan",
    "SubscriptionStatus",
]
