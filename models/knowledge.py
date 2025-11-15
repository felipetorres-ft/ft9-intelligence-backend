# models/knowledge.py — FT9 Intelligence
# Versão AI9 Patch 3 — VECTOR removido (pgvector não disponível no Railway)

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from database import Base

class Knowledge(Base):
    __tablename__ = "knowledge"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)
    content = Column(Text, nullable=False)

    # REMOVIDO: pgvector → não suportado no Railway
    # embedding = Column(VECTOR(1536))
    embedding = Column(Text)  # JSON string ou lista serializada

    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
