"""
Payment Router - Mercado Pago Integration
Created by: AI9 Architecture
Date: 2025-11-16
"""

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
import httpx
import os
import logging

from database.db import get_db
from services.payment_service import (
    save_payment,
    update_payment_status,
    get_payment_by_id,
    get_payment_by_preference_id
)
from payment.mercadopago_config import get_mp_sdk

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/payment", tags=["Payment"])


# Pydantic Models
class CreatePaymentRequest(BaseModel):
    amount: int
    title: str
    description: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Optional[dict] = None


class PaymentResponse(BaseModel):
    id: str
    preference_id: str
    status: str
    amount: int
    init_point: Optional[str] = None


@router.post("/create", response_model=PaymentResponse)
async def create_payment(
    payment_data: CreatePaymentRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    Create a new payment preference with Mercado Pago
    Returns the payment URL for checkout
    """
    try:
        # Get Mercado Pago SDK
        sdk = get_mp_sdk()
        
        # Create preference data
        preference_data = {
            "items": [
                {
                    "title": payment_data.title,
                    "description": payment_data.description or payment_data.title,
                    "quantity": 1,
                    "currency_id": "BRL",
                    "unit_price": float(payment_data.amount)
                }
            ],
            "back_urls": {
                "success": os.getenv("MP_SUCCESS_URL", "https://ft9.com/sucesso"),
                "failure": os.getenv("MP_FAILURE_URL", "https://ft9.com/erro"),
                "pending": os.getenv("MP_FAILURE_URL", "https://ft9.com/erro")
            },
            "auto_return": "approved",
            "notification_url": os.getenv("MP_WEBHOOK_URL", "https://api.ft9.com/api/v1/payment/webhook"),
            "external_reference": payment_data.user_id or "no_user"
        }
        
        # Create preference
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]
        
        # Save to database
        payment_db_data = {
            "preference_id": preference["id"],
            "status": "pending",
            "amount": payment_data.amount,
            "user_id": payment_data.user_id,
            "metadata": payment_data.metadata or {}
        }
        
        payment = await save_payment(session, payment_db_data)
        
        logger.info(f"✅ Payment created: {payment.id} | Preference: {preference['id']}")
        
        return PaymentResponse(
            id=str(payment.id),
            preference_id=payment.preference_id,
            status=payment.status,
            amount=payment.amount,
            init_point=preference.get("init_point")
        )
        
    except Exception as e:
        logger.error(f"❌ Error creating payment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating payment: {str(e)}")


async def notify_ft9_flow(preference_id: str, payment_id: str, status: str):
    """Notify FT9-Flow about payment status"""
    try:
        if status == "approved":
            url = os.getenv("FT9_FLOW_PAYMENT_APPROVED", "")
        else:
            url = os.getenv("FT9_FLOW_PAYMENT_REJECTED", "")
        
        if not url:
            logger.warning("⚠️ FT9-Flow URL not configured")
            return
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={
                    "preference_id": preference_id,
                    "payment_id": payment_id,
                    "status": status
                },
                timeout=10.0
            )
            logger.info(f"📡 FT9-Flow notified: {status} | Response: {response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Error notifying FT9-Flow: {str(e)}")


@router.post("/webhook")
async def payment_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db)
):
    """
    Receive Mercado Pago webhook notifications
    """
    try:
        # Get webhook data
        body = await request.json()
        logger.info(f"📥 Webhook received: {body}")
        
        # Extract payment info
        if body.get("type") != "payment":
            return {"status": "ignored"}
        
        payment_id = body.get("data", {}).get("id")
        
        if not payment_id:
            logger.warning("⚠️ No payment ID in webhook")
            return {"status": "no_payment_id"}
        
        # Get payment details from Mercado Pago
        sdk = get_mp_sdk()
        payment_info = sdk.payment().get(payment_id)
        payment_data = payment_info["response"]
        
        # Extract preference_id
        preference_id = payment_data.get("external_reference") or payment_data.get("metadata", {}).get("preference_id")
        
        if not preference_id:
            logger.warning(f"⚠️ No preference_id for payment {payment_id}")
            return {"status": "no_preference_id"}
        
        # Update payment status
        status = payment_data.get("status")
        await update_payment_status(session, preference_id, str(payment_id), status)
        
        logger.info(f"✅ Payment updated: {preference_id} | Status: {status}")
        
        # Notify FT9-Flow in background
        background_tasks.add_task(notify_ft9_flow, preference_id, str(payment_id), status)
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {str(e)}")
        return {"status": "error", "message": str(e)}


@router.get("/status/{payment_id}")
async def get_payment_status(
    payment_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Get payment status by ID
    """
    try:
        payment = await get_payment_by_id(session, payment_id)
        
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        return {
            "id": str(payment.id),
            "preference_id": payment.preference_id,
            "mp_payment_id": payment.mp_payment_id,
            "status": payment.status,
            "amount": payment.amount,
            "created_at": payment.created_at.isoformat(),
            "updated_at": payment.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting payment status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
