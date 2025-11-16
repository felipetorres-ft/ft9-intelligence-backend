"""
Serviço de Billing e Pagamentos com Stripe
"""
import stripe
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import Organization
from database.models import SubscriptionPlan, SubscriptionStatus
from config import settings
import logging

logger = logging.getLogger(__name__)

# Configurar Stripe
stripe.api_key = settings.stripe_secret_key


class BillingService:
    """
    Serviço para gerenciar billing e pagamentos via Stripe
    """
    
    # Mapeamento de planos para IDs de preços do Stripe
    PRICE_IDS = {
        SubscriptionPlan.STARTER: settings.stripe_price_starter,
        SubscriptionPlan.PROFESSIONAL: settings.stripe_price_professional,
        SubscriptionPlan.ENTERPRISE: settings.stripe_price_enterprise
    }
    
    async def create_customer(
        self,
        organization: Organization,
        payment_method_id: Optional[str] = None
    ) -> str:
        """
        Criar cliente no Stripe
        """
        try:
            customer_data = {
                "name": organization.name,
                "email": organization.email,
                "phone": organization.phone,
                "metadata": {
                    "organization_id": organization.id,
                    "organization_slug": organization.slug
                }
            }
            
            if payment_method_id:
                customer_data["payment_method"] = payment_method_id
                customer_data["invoice_settings"] = {
                    "default_payment_method": payment_method_id
                }
            
            customer = await asyncio.to_thread(stripe.Customer.create, **customer_data)
            
            logger.info(f"Cliente Stripe criado: {customer.id} para org {organization.id}")
            
            return customer.id
        
        except Exception as e:
            logger.error(f"Erro ao criar cliente Stripe: {e}")
            raise
    
    async def create_subscription(
        self,
        db: AsyncSession,
        organization: Organization,
        plan: SubscriptionPlan,
        payment_method_id: Optional[str] = None,
        trial_days: int = 14
    ) -> Dict[str, Any]:
        """
        Criar assinatura no Stripe
        """
        try:
            # Criar ou obter customer
            if not organization.stripe_customer_id:
                customer_id = await self.create_customer(organization, payment_method_id)
                organization.stripe_customer_id = customer_id
                await db.commit()
            else:
                customer_id = organization.stripe_customer_id
            
            # Obter price_id do plano
            price_id = self.PRICE_IDS.get(plan)
            if not price_id:
                raise ValueError(f"Plano inválido: {plan}")
            
            # Criar assinatura
            subscription_data = {
                "customer": customer_id,
                "items": [{"price": price_id}],
                "metadata": {
                    "organization_id": organization.id,
                    "organization_slug": organization.slug
                }
            }
            
            # Adicionar trial se especificado
            if trial_days > 0:
                subscription_data["trial_period_days"] = trial_days
            
            # Adicionar payment method se fornecido
            if payment_method_id:
                subscription_data["default_payment_method"] = payment_method_id
            
            subscription = await asyncio.to_thread(stripe.Subscription.create, **subscription_data)
            
            # Atualizar organização
            organization.stripe_subscription_id = subscription.id
            organization.subscription_plan = plan
            organization.subscription_status = SubscriptionStatus.TRIAL if trial_days > 0 else SubscriptionStatus.ACTIVE
            organization.subscription_started_at = datetime.utcnow()
            
            if trial_days > 0:
                organization.subscription_expires_at = datetime.utcnow() + timedelta(days=trial_days)
            
            await db.commit()
            
            logger.info(f"Assinatura criada: {subscription.id} para org {organization.id}")
            
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "current_period_end": subscription.current_period_end,
                "trial_end": subscription.trial_end
            }
        
        except Exception as e:
            logger.error(f"Erro ao criar assinatura: {e}")
            raise
    
    async def cancel_subscription(
        self,
        db: AsyncSession,
        organization: Organization,
        at_period_end: bool = True
    ) -> Dict[str, Any]:
        """
        Cancelar assinatura
        """
        try:
            if not organization.stripe_subscription_id:
                raise ValueError("Organização não possui assinatura ativa")
            
            subscription = stripe.Subscription.modify(
                organization.stripe_subscription_id,
                cancel_at_period_end=at_period_end
            )
            
            if not at_period_end:
                organization.subscription_status = SubscriptionStatus.CANCELED
                await db.commit()
            
            logger.info(f"Assinatura cancelada: {subscription.id}")
            
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "canceled_at": subscription.canceled_at
            }
        
        except Exception as e:
            logger.error(f"Erro ao cancelar assinatura: {e}")
            raise
    
    async def update_subscription(
        self,
        db: AsyncSession,
        organization: Organization,
        new_plan: SubscriptionPlan
    ) -> Dict[str, Any]:
        """
        Atualizar plano da assinatura (upgrade/downgrade)
        """
        try:
            if not organization.stripe_subscription_id:
                raise ValueError("Organização não possui assinatura ativa")
            
            # Obter assinatura atual
            subscription = stripe.Subscription.retrieve(organization.stripe_subscription_id)
            
            # Obter novo price_id
            new_price_id = self.PRICE_IDS.get(new_plan)
            if not new_price_id:
                raise ValueError(f"Plano inválido: {new_plan}")
            
            # Atualizar assinatura
            updated_subscription = stripe.Subscription.modify(
                organization.stripe_subscription_id,
                items=[{
                    "id": subscription["items"]["data"][0].id,
                    "price": new_price_id
                }],
                proration_behavior="always_invoice"
            )
            
            # Atualizar organização
            organization.subscription_plan = new_plan
            await db.commit()
            
            logger.info(f"Assinatura atualizada: {updated_subscription.id} para plano {new_plan}")
            
            return {
                "subscription_id": updated_subscription.id,
                "status": updated_subscription.status,
                "plan": new_plan.value
            }
        
        except Exception as e:
            logger.error(f"Erro ao atualizar assinatura: {e}")
            raise
    
    async def create_portal_session(
        self,
        organization: Organization,
        return_url: str
    ) -> str:
        """
        Criar sessão do portal do cliente Stripe
        """
        try:
            if not organization.stripe_customer_id:
                raise ValueError("Organização não possui cliente Stripe")
            
            session = stripe.billing_portal.Session.create(
                customer=organization.stripe_customer_id,
                return_url=return_url
            )
            
            logger.info(f"Portal session criada para org {organization.id}")
            
            return session.url
        
        except Exception as e:
            logger.error(f"Erro ao criar portal session: {e}")
            raise
    
    async def handle_webhook_event(
        self,
        db: AsyncSession,
        event: Dict[str, Any]
    ) -> None:
        """
        Processar evento de webhook do Stripe
        """
        event_type = event["type"]
        data = event["data"]["object"]
        
        logger.info(f"Processando webhook: {event_type}")
        
        try:
            if event_type == "customer.subscription.created":
                await self._handle_subscription_created(db, data)
            
            elif event_type == "customer.subscription.updated":
                await self._handle_subscription_updated(db, data)
            
            elif event_type == "customer.subscription.deleted":
                await self._handle_subscription_deleted(db, data)
            
            elif event_type == "invoice.payment_succeeded":
                await self._handle_payment_succeeded(db, data)
            
            elif event_type == "invoice.payment_failed":
                await self._handle_payment_failed(db, data)
            
            else:
                logger.info(f"Evento não processado: {event_type}")
        
        except Exception as e:
            logger.error(f"Erro ao processar webhook: {e}")
            raise
    
    async def _handle_subscription_created(
        self,
        db: AsyncSession,
        subscription: Dict[str, Any]
    ) -> None:
        """Processar criação de assinatura"""
        org_id = subscription["metadata"].get("organization_id")
        if not org_id:
            return
        
        result = await db.execute(
            select(Organization).where(Organization.id == int(org_id))
        )
        organization = result.scalar_one_or_none()
        
        if organization:
            organization.subscription_status = SubscriptionStatus.ACTIVE
            await db.commit()
            logger.info(f"Assinatura ativada para org {org_id}")
    
    async def _handle_subscription_updated(
        self,
        db: AsyncSession,
        subscription: Dict[str, Any]
    ) -> None:
        """Processar atualização de assinatura"""
        org_id = subscription["metadata"].get("organization_id")
        if not org_id:
            return
        
        result = await db.execute(
            select(Organization).where(Organization.id == int(org_id))
        )
        organization = result.scalar_one_or_none()
        
        if organization:
            status = subscription["status"]
            if status == "active":
                organization.subscription_status = SubscriptionStatus.ACTIVE
            elif status == "past_due":
                organization.subscription_status = SubscriptionStatus.PAST_DUE
            elif status == "canceled":
                organization.subscription_status = SubscriptionStatus.CANCELED
            
            await db.commit()
            logger.info(f"Status de assinatura atualizado para org {org_id}: {status}")
    
    async def _handle_subscription_deleted(
        self,
        db: AsyncSession,
        subscription: Dict[str, Any]
    ) -> None:
        """Processar cancelamento de assinatura"""
        org_id = subscription["metadata"].get("organization_id")
        if not org_id:
            return
        
        result = await db.execute(
            select(Organization).where(Organization.id == int(org_id))
        )
        organization = result.scalar_one_or_none()
        
        if organization:
            organization.subscription_status = SubscriptionStatus.CANCELED
            organization.is_active = False
            await db.commit()
            logger.info(f"Assinatura cancelada para org {org_id}")
    
    async def _handle_payment_succeeded(
        self,
        db: AsyncSession,
        invoice: Dict[str, Any]
    ) -> None:
        """Processar pagamento bem-sucedido"""
        subscription_id = invoice.get("subscription")
        if not subscription_id:
            return
        
        result = await db.execute(
            select(Organization).where(Organization.stripe_subscription_id == subscription_id)
        )
        organization = result.scalar_one_or_none()
        
        if organization:
            organization.subscription_status = SubscriptionStatus.ACTIVE
            organization.is_active = True
            await db.commit()
            logger.info(f"Pagamento processado para org {organization.id}")
    
    async def _handle_payment_failed(
        self,
        db: AsyncSession,
        invoice: Dict[str, Any]
    ) -> None:
        """Processar falha de pagamento"""
        subscription_id = invoice.get("subscription")
        if not subscription_id:
            return
        
        result = await db.execute(
            select(Organization).where(Organization.stripe_subscription_id == subscription_id)
        )
        organization = result.scalar_one_or_none()
        
        if organization:
            organization.subscription_status = SubscriptionStatus.PAST_DUE
            await db.commit()
            logger.warning(f"Falha no pagamento para org {organization.id}")


# Instância global do serviço
billing_service = BillingService()
