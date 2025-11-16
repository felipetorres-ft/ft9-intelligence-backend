"""
Router administrativo para setup inicial
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.database import get_db
from database.models import Organization, SubscriptionPlan, SubscriptionStatus
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.post("/setup-organization")
async def setup_organization(db: AsyncSession = Depends(get_db)):
    """
    Cria a Organization para o número de teste do WhatsApp
    """
    try:
        # Verificar se já existe
        result = await db.execute(
            select(Organization).where(Organization.slug == "ft9-test")
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            logger.info(f"Organization já existe: {existing.name}")
            return {
                "status": "already_exists",
                "organization": {
                    "id": existing.id,
                    "name": existing.name,
                    "slug": existing.slug,
                    "whatsapp_phone_number_id": existing.whatsapp_phone_number_id
                }
            }
        
        # Criar nova organization
        org = Organization(
            name="FT9 Intelligence - Test Number",
            slug="ft9-test",
            email="test@ft9intelligence.com",
            phone="+15551667990",
            whatsapp_phone_number="+15551667990",
            whatsapp_phone_number_id="830615479241121",
            whatsapp_business_account_id="WHATSAPP_BUSINESS_ACCOUNT_ID",
            subscription_plan=SubscriptionPlan.STARTER,
            subscription_status=SubscriptionStatus.TRIAL,
            is_active=True
        )
        
        db.add(org)
        await db.commit()
        await db.refresh(org)
        
        logger.info(f"Organization criada com sucesso: {org.name}")
        
        return {
            "status": "created",
            "organization": {
                "id": org.id,
                "name": org.name,
                "slug": org.slug,
                "whatsapp_phone_number_id": org.whatsapp_phone_number_id
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao criar organization: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
