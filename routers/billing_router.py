"""
Rotas de Billing e Pagamentos
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from database import get_db, User, Organization
from database.models import SubscriptionPlan, UserRole
from auth import get_current_active_user, require_role
from services import billing_service
from pydantic import BaseModel
import stripe
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/billing", tags=["Billing"])


class CreateSubscriptionRequest(BaseModel):
    plan: SubscriptionPlan
    payment_method_id: Optional[str] = None
    trial_days: int = 14


class UpdateSubscriptionRequest(BaseModel):
    new_plan: SubscriptionPlan


class CancelSubscriptionRequest(BaseModel):
    at_period_end: bool = True


@router.post("/subscription")
async def create_subscription(
    request: CreateSubscriptionRequest,
    current_user: User = Depends(require_role([UserRole.ORG_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """
    Criar assinatura para a organização (apenas admin)
    
    **TEMPORARIAMENTE DESATIVADO** - Funcionalidade em construção.
    Aguardando configuração completa da integração de pagamentos.
    """
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Funcionalidade de assinaturas temporariamente indisponível. Em breve estará disponível."
    )


@router.patch("/subscription")
async def update_subscription(
    request: UpdateSubscriptionRequest,
    current_user: User = Depends(require_role([UserRole.ORG_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """
    Atualizar plano da assinatura (upgrade/downgrade)
    
    **TEMPORARIAMENTE DESATIVADO** - Funcionalidade em construção.
    Aguardando configuração completa da integração de pagamentos.
    """
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Funcionalidade de assinaturas temporariamente indisponível. Em breve estará disponível."
    )


@router.delete("/subscription")
async def cancel_subscription(
    request: CancelSubscriptionRequest,
    current_user: User = Depends(require_role([UserRole.ORG_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancelar assinatura
    
    **TEMPORARIAMENTE DESATIVADO** - Funcionalidade em construção.
    Aguardando configuração completa da integração de pagamentos.
    """
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Funcionalidade de assinaturas temporariamente indisponível. Em breve estará disponível."
    )


@router.get("/portal")
async def get_portal_url(
    return_url: str,
    current_user: User = Depends(require_role([UserRole.ORG_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """
    Obter URL do portal do cliente Stripe
    
    **TEMPORARIAMENTE DESATIVADO** - Funcionalidade em construção.
    Aguardando configuração completa da integração de pagamentos.
    """
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Funcionalidade de portal de assinaturas temporariamente indisponível. Em breve estará disponível."
    )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook do Stripe para processar eventos
    """
    try:
        from config import settings
        
        # Obter payload
        payload = await request.body()
        
        # Verificar assinatura
        try:
            event = stripe.Webhook.construct_event(
                payload,
                stripe_signature,
                settings.stripe_webhook_secret
            )
        except ValueError as e:
            logger.error(f"Payload inválido: {e}")
            raise HTTPException(status_code=400, detail="Payload inválido")
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Assinatura inválida: {e}")
            raise HTTPException(status_code=400, detail="Assinatura inválida")
        
        # Processar evento
        await billing_service.handle_webhook_event(db, event)
        
        return {"success": True}
    
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/plans")
async def get_plans():
    """
    Listar planos disponíveis
    """
    return {
        "plans": [
            {
                "id": "starter",
                "name": "Starter",
                "price": 497,
                "currency": "BRL",
                "interval": "month",
                "features": [
                    "1.000 mensagens/mês",
                    "1 usuário",
                    "Suporte por email",
                    "WhatsApp Business API",
                    "IA básica"
                ]
            },
            {
                "id": "professional",
                "name": "Professional",
                "price": 997,
                "currency": "BRL",
                "interval": "month",
                "features": [
                    "5.000 mensagens/mês",
                    "5 usuários",
                    "Suporte prioritário",
                    "WhatsApp Business API",
                    "IA avançada com memória",
                    "Automações básicas",
                    "Dashboard analytics"
                ]
            },
            {
                "id": "enterprise",
                "name": "Enterprise",
                "price": 2997,
                "currency": "BRL",
                "interval": "month",
                "features": [
                    "Mensagens ilimitadas",
                    "Usuários ilimitados",
                    "Suporte 24/7",
                    "WhatsApp Business API",
                    "IA avançada com RAG",
                    "Automações avançadas",
                    "Dashboard analytics",
                    "API dedicada",
                    "White-label"
                ]
            }
        ]
    }
