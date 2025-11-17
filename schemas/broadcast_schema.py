"""
FT9 Intelligence - Broadcast Schema
Schemas Pydantic para o sistema de broadcast massivo via Z-API
"""

from pydantic import BaseModel
from typing import Optional


class BroadcastResponse(BaseModel):
    """Response para inicialização de broadcast"""
    message: str


class BroadcastStatus(BaseModel):
    """Status de um broadcast em andamento"""
    total_contacts: int
    sent: int
    failed: int
    pending: int
    status: str  # "running", "completed", "failed"


class ContactInfo(BaseModel):
    """Informações de um contato para broadcast"""
    nome: str
    numero: str
    clinica: Optional[str] = "FT9"
