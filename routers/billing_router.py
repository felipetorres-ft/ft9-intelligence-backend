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
    """
    try:
        # Buscar organização
        from sqlalchemy import select
        result = await db.execute(
            select(Organization).where(Organization.id == current_user.organization_id)
        )
        organization = result.scalar_one_or_none()
        
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organização não encontrada"
            )
        
        # Verificar se já possui assinatura
        if organization.stripe_subscription_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organização já possui assinatura ativa"
            )
        
        # Criar assinatura
        subscription_data = await billing_service.create_subscription(
            db=db,
            organization=organization,
            plan=request.plan,
            payment_method_id=request.payment_method_id,
            trial_days=request.trial_days
        )
        
        return {
            "success": True,
            "subscription": subscription_data
        }
    
    except Exception as e:
        logger.error(f"Erro ao criar assinatura: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/subscription")
async def update_subscription(
    request: UpdateSubscriptionRequest,
    current_user: User = Depends(require_role([UserRole.ORG_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """
    Atualizar plano da assinatura (upgrade/downgrade)
    """
    try:
        # Buscar organização
        from sqlalchemy import select
        result = await db.execute(
            select(Organization).where(Organization.id == current_user.organization_id)
        )
        organization = result.scalar_one_or_none()
        
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organização não encontrada"
            )
        
        # Atualizar assinatura
        subscription_data = await billing_service.update_subscription(
            db=db,
            organization=organization,
            new_plan=request.new_plan
        )
        
        return {
            "success": True,
            "subscription": subscription_data
        }
    
    except Exception as e:
        logger.error(f"Erro ao atualizar assinatura: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/subscription")
async def cancel_subscription(
    request: CancelSubscriptionRequest,
    current_user: User = Depends(require_role([UserRole.ORG_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancelar assinatura
    """
    try:
        # Buscar organização
        from sqlalchemy import select
        result = await db.execute(
            select(Organization).where(Organization.id == current_user.organization_id)
        )
        organization = result.scalar_one_or_none()
        
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organização não encontrada"
            )
        
        # Cancelar assinatura
        subscription_data = await billing_service.cancel_subscription(
            db=db,
            organization=organization,
            at_period_end=request.at_period_end
        )
        
        return {
            "success": True,
            "subscription": subscription_data
        }
    
    except Exception as e:
        logger.error(f"Erro ao cancelar assinatura: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/portal")
async def get_portal_url(
    return_url: str,
    current_user: User = Depends(require_role([UserRole.ORG_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """
    Obter URL do portal do cliente Stripe
    """
    try:
        # Buscar organização
        from sqlalchemy import select
        result = await db.execute(
            select(Organization).where(Organization.id == current_user.organization_id)
        )
        organization = result.scalar_one_or_none()
        
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organização não encontrada"
            )
        
        # Criar portal session
        portal_url = await billing_service.create_portal_session(
            organization=organization,
            return_url=return_url
        )
        
        return {
            "url": portal_url
        }
    
    except Exception as e:
        logger.error(f"Erro ao criar portal session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
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
