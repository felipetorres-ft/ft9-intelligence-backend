# models/knowledge.py — FT9 Intelligence
# Versão AI9 — Tabela Knowledge com suporte a pgvector

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import VECTOR
from database import Base

class Knowledge(Base):
    __tablename__ = "knowledge"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)
    content = Column(Text, nullable=False)
    
    # Embedding (1536 dimensões — modelo OpenAI)
    embedding = Column(VECTOR(1536))
    
    # Multi-tenant (organização)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
