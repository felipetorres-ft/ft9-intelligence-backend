"""
Modelos de banco de dados para sistema multi-tenant FT9
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    """Roles de usuário no sistema"""
    SUPER_ADMIN = "super_admin"  # Administrador da plataforma FT9
    ORG_ADMIN = "org_admin"      # Administrador da organização
    ORG_MANAGER = "org_manager"  # Gerente da organização
    ORG_AGENT = "org_agent"      # Agente/Atendente


class SubscriptionPlan(str, enum.Enum):
    """Planos de assinatura"""
    STARTER = "starter"          # R$ 497/mês
    PROFESSIONAL = "professional" # R$ 997/mês
    ENTERPRISE = "enterprise"     # R$ 2.997/mês


class SubscriptionStatus(str, enum.Enum):
    """Status da assinatura"""
    TRIAL = "trial"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    SUSPENDED = "suspended"


class Organization(Base):
    """
    Organização (Tenant) - Clínica, Escola, Loja, etc.
    """
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    
    # Informações de contato
    email = Column(String(255), nullable=False)
    phone = Column(String(20))
    
    # Endereço
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(2))
    country = Column(String(2), default="BR")
    
    # Assinatura
    subscription_plan = Column(SQLEnum(SubscriptionPlan), default=SubscriptionPlan.STARTER)
    subscription_status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.TRIAL)
    subscription_started_at = Column(DateTime(timezone=True))
    subscription_expires_at = Column(DateTime(timezone=True))
    
    # Stripe
    stripe_customer_id = Column(String(100), unique=True)
    stripe_subscription_id = Column(String(100), unique=True)
    
    # Configurações
    whatsapp_phone_number = Column(String(20))
    whatsapp_phone_number_id = Column(String(100))
    whatsapp_business_account_id = Column(String(100))
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="organization", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Organization {self.name} ({self.slug})>"


class User(Base):
    """
    Usuário do sistema (pertence a uma organização)
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Credenciais
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Informações pessoais
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20))
    
    # Permissões
    role = Column(SQLEnum(UserRole), default=UserRole.ORG_AGENT)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Metadata
    last_login_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    organization = relationship("Organization", back_populates="users")
    
    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class Conversation(Base):
    """
    Conversa com cliente via WhatsApp
    """
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Identificação do cliente
    customer_phone = Column(String(20), nullable=False, index=True)
    customer_name = Column(String(255))
    
    # Status
    is_active = Column(Boolean, default=True)
    is_archived = Column(Boolean, default=False)
    
    # Metadata
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    last_message_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))
    
    # Relacionamentos
    organization = relationship("Organization", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation {self.customer_phone} (Org: {self.organization_id})>"


class Message(Base):
    """
    Mensagem individual dentro de uma conversa
    """
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    
    # Conteúdo
    message_type = Column(String(20), default="text")  # text, image, audio, video, document
    content = Column(Text, nullable=False)
    
    # Direção
    is_from_customer = Column(Boolean, default=True)
    
    # WhatsApp IDs
    whatsapp_message_id = Column(String(100), unique=True)
    
    # Metadata
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    delivered_at = Column(DateTime(timezone=True))
    read_at = Column(DateTime(timezone=True))
    
    # Relacionamentos
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        direction = "from" if self.is_from_customer else "to"
        return f"<Message {direction} customer (Conv: {self.conversation_id})>"


class KnowledgeBase(Base):
    """
    Base de conhecimento para RAG (FT9-Memory)
    """
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Conteúdo
    title = Column(String(500))
    content = Column(Text, nullable=False)
    source = Column(String(500))  # URL, arquivo, etc.
    
    # Embeddings (armazenado como JSON string)
    embedding = Column(Text)  # Será usado com FAISS/Milvus
    
    # Categorização
    category = Column(String(100))
    tags = Column(Text)  # JSON array de tags
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<KnowledgeBase {self.title} (Org: {self.organization_id})>"
