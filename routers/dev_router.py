"""
Router temporário para desenvolvimento - Geração de hash de senha
ATENÇÃO: Este router deve ser REMOVIDO após gerar o hash necessário
"""

from fastapi import APIRouter
from pydantic import BaseModel
from core.security import get_password_hash

router = APIRouter(prefix="/dev", tags=["Dev"])


class PasswordRequest(BaseModel):
    password: str


@router.post("/hash")
def dev_hash(request: PasswordRequest):
    """
    Endpoint temporário para gerar hash de senha usando a mesma função do backend.
    
    ⚠️ USAR APENAS EM DESENVOLVIMENTO
    ⚠️ REMOVER APÓS GERAR O HASH NECESSÁRIO
    """
    return {"hash": get_password_hash(request.password)}
