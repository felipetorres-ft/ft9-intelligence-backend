"""
Rotas de Automações (FT9-Flow)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any
from database import get_db, User
from auth import get_current_active_user
from services.automation_service import automation_service
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/automations", tags=["Automations"])


class CreateAutomationRequest(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_type: str
    trigger_config: Dict[str, Any]
    actions: List[Dict[str, Any]]
    conditions: Optional[List[Dict[str, Any]]] = None


class ExecuteAutomationRequest(BaseModel):
    input_data: Dict[str, Any]


@router.post("/")
async def create_automation(
    request: CreateAutomationRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Criar nova automação
    """
    try:
        automation_id = await automation_service.create_automation(
            db=db,
            organization_id=current_user.organization_id,
            name=request.name,
            description=request.description,
            trigger_type=request.trigger_type,
            trigger_config=request.trigger_config,
            actions=request.actions,
            conditions=request.conditions
        )
        
        return {
            "success": True,
            "automation_id": automation_id
        }
    
    except Exception as e:
        logger.error(f"Erro ao criar automação: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/")
async def list_automations(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Listar automações da organização
    """
    try:
        from sqlalchemy import select
        from database.automation_models import Automation
        
        result = await db.execute(
            select(Automation).where(
                Automation.organization_id == current_user.organization_id
            )
        )
        automations = result.scalars().all()
        
        return {
            "automations": [
                {
                    "id": a.id,
                    "name": a.name,
                    "description": a.description,
                    "trigger_type": a.trigger_type,
                    "is_active": a.is_active,
                    "execution_count": a.execution_count,
                    "last_executed_at": a.last_executed_at.isoformat() if a.last_executed_at else None,
                    "created_at": a.created_at.isoformat() if a.created_at else None
                }
                for a in automations
            ]
        }
    
    except Exception as e:
        logger.error(f"Erro ao listar automações: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{automation_id}")
async def get_automation(
    automation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obter detalhes de uma automação
    """
    try:
        from sqlalchemy import select
        from database.automation_models import Automation
        
        result = await db.execute(
            select(Automation).where(
                Automation.id == automation_id,
                Automation.organization_id == current_user.organization_id
            )
        )
        automation = result.scalar_one_or_none()
        
        if not automation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automação não encontrada"
            )
        
        return {
            "id": automation.id,
            "name": automation.name,
            "description": automation.description,
            "trigger_type": automation.trigger_type,
            "trigger_config": automation.trigger_config,
            "conditions": automation.conditions,
            "actions": automation.actions,
            "is_active": automation.is_active,
            "execution_count": automation.execution_count,
            "last_executed_at": automation.last_executed_at.isoformat() if automation.last_executed_at else None,
            "created_at": automation.created_at.isoformat() if automation.created_at else None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter automação: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{automation_id}/execute")
async def execute_automation(
    automation_id: int,
    request: ExecuteAutomationRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Executar automação manualmente
    """
    try:
        result = await automation_service.execute_automation(
            db=db,
            automation_id=automation_id,
            input_data=request.input_data
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Erro ao executar automação: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/{automation_id}/toggle")
async def toggle_automation(
    automation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Ativar/desativar automação
    """
    try:
        from sqlalchemy import select
        from database.automation_models import Automation
        
        result = await db.execute(
            select(Automation).where(
                Automation.id == automation_id,
                Automation.organization_id == current_user.organization_id
            )
        )
        automation = result.scalar_one_or_none()
        
        if not automation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automação não encontrada"
            )
        
        automation.is_active = not automation.is_active
        await db.commit()
        
        return {
            "success": True,
            "is_active": automation.is_active
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao alternar automação: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{automation_id}")
async def delete_automation(
    automation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Deletar automação
    """
    try:
        from sqlalchemy import select
        from database.automation_models import Automation
        
        result = await db.execute(
            select(Automation).where(
                Automation.id == automation_id,
                Automation.organization_id == current_user.organization_id
            )
        )
        automation = result.scalar_one_or_none()
        
        if not automation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automação não encontrada"
            )
        
        await db.delete(automation)
        await db.commit()
        
        return {
            "success": True,
            "message": "Automação deletada com sucesso"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar automação: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/templates/list")
async def list_templates():
    """
    Listar templates de automação prontos
    """
    return {
        "templates": [
            {
                "id": "welcome_message",
                "name": "Mensagem de Boas-Vindas",
                "description": "Enviar mensagem automática quando novo contato iniciar conversa",
                "trigger_type": "conversation_started",
                "actions": [
                    {
                        "type": "send_whatsapp_message",
                        "config": {
                            "message": "Olá! Bem-vindo à {organization_name}. Como posso ajudar?"
                        }
                    }
                ]
            },
            {
                "id": "follow_up_3days",
                "name": "Follow-up após 3 dias",
                "description": "Enviar mensagem de follow-up 3 dias após última interação",
                "trigger_type": "scheduled",
                "trigger_config": {
                    "delay_days": 3
                },
                "actions": [
                    {
                        "type": "send_whatsapp_message",
                        "config": {
                            "message": "Olá! Gostaria de saber se ainda tem alguma dúvida sobre nossos serviços."
                        }
                    }
                ]
            },
            {
                "id": "payment_reminder",
                "name": "Lembrete de Pagamento",
                "description": "Enviar lembrete quando pagamento estiver atrasado",
                "trigger_type": "payment_failed",
                "actions": [
                    {
                        "type": "send_whatsapp_message",
                        "config": {
                            "message": "Olá! Identificamos um problema com seu pagamento. Por favor, atualize seus dados de pagamento."
                        }
                    }
                ]
            },
            {
                "id": "ai_auto_response",
                "name": "Resposta Automática com IA",
                "description": "Responder automaticamente usando IA quando mensagem for recebida",
                "trigger_type": "message_received",
                "actions": [
                    {
                        "type": "ai_generate",
                        "config": {
                            "prompt": "Responda a seguinte mensagem de forma profissional: {message}"
                        }
                    },
                    {
                        "type": "send_whatsapp_message",
                        "config": {
                            "message": "{ai_response}"
                        }
                    }
                ]
            }
        ]
    }
