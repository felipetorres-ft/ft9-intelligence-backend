"""
Modelo Knowledge para Base de Conhecimento com pgvector
Implementado conforme especificação dos programadores - 15/11/2025
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, func
from sqlalchemy.dialects.postgresql import VECTOR
from sqlalchemy.orm import relationship
from database.models import Base


class Knowledge(Base):
    """
    Modelo de conhecimento para RAG com embeddings vetoriais
    Usa pgvector para busca semântica eficiente
    """
    __tablename__ = "knowledge"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=True, index=True)
    content = Column(Text, nullable=False)
    
    # Embedding vetorial (1536 dimensões para text-embedding-ada-002)
    embedding = Column(VECTOR(1536), nullable=True)
    
    # Multi-tenant: cada documento pertence a uma organização
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Metadata
    source = Column(String(500), nullable=True)  # URL, arquivo, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Knowledge {self.title} (Org: {self.organization_id})>"
    
    def to_dict(self):
        """Serialização para JSON"""
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "content": self.content,
            "organization_id": self.organization_id,
            "source": self.source,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
