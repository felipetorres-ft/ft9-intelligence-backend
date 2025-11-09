"""
Schemas Pydantic para validação de dados da API
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from database.models import UserRole, SubscriptionPlan, SubscriptionStatus


# ============================================================================
# SCHEMAS DE AUTENTICAÇÃO
# ============================================================================

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ============================================================================
# SCHEMAS DE ORGANIZAÇÃO
# ============================================================================

class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    # Admin user data
    admin_email: EmailStr
    admin_password: str = Field(..., min_length=8)
    admin_full_name: str = Field(..., min_length=3)


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    whatsapp_phone_number: Optional[str] = None


class OrganizationResponse(OrganizationBase):
    id: int
    slug: str
    subscription_plan: SubscriptionPlan
    subscription_status: SubscriptionStatus
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# SCHEMAS DE USUÁRIO
# ============================================================================

class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=3, max_length=255)
    phone: Optional[str] = None
    role: UserRole = UserRole.ORG_AGENT


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    organization_id: int


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    organization_id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# SCHEMAS DE CONVERSA
# ============================================================================

class ConversationBase(BaseModel):
    customer_phone: str
    customer_name: Optional[str] = None


class ConversationCreate(ConversationBase):
    organization_id: int


class ConversationResponse(ConversationBase):
    id: int
    organization_id: int
    is_active: bool
    is_archived: bool
    started_at: datetime
    last_message_at: datetime
    ended_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# SCHEMAS DE MENSAGEM
# ============================================================================

class MessageBase(BaseModel):
    content: str
    message_type: str = "text"
    is_from_customer: bool = True


class MessageCreate(MessageBase):
    conversation_id: int
    whatsapp_message_id: Optional[str] = None


class MessageResponse(MessageBase):
    id: int
    conversation_id: int
    sent_at: datetime
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# SCHEMAS DE BASE DE CONHECIMENTO
# ============================================================================

class KnowledgeBaseCreate(BaseModel):
    title: Optional[str] = None
    content: str
    source: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class KnowledgeBaseResponse(BaseModel):
    id: int
    organization_id: int
    title: Optional[str] = None
    content: str
    source: Optional[str] = None
    category: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# SCHEMAS DE WEBHOOK
# ============================================================================

class WebhookMessage(BaseModel):
    """Schema para mensagem recebida do WhatsApp"""
    from_number: str
    message_body: str
    message_id: str
    timestamp: str
