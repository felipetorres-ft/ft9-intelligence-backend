"""
Payment Model - Mercado Pago Integration
Created by: AI9 Architecture
Date: 2025-11-16
"""

from sqlalchemy import Column, String, Integer, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from database.models import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    preference_id = Column(String(255), nullable=False, unique=True, index=True)
    mp_payment_id = Column(String(255), nullable=True, index=True)
    status = Column(String(50), nullable=False, index=True)
    amount = Column(Integer, nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Payment(id={self.id}, preference_id={self.preference_id}, status={self.status})>"
