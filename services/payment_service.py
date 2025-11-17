"""
Payment Service - Business Logic
Created by: AI9 Architecture
Date: 2025-11-16
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from database.payment_model import Payment
import uuid


async def save_payment(session: AsyncSession, data: dict):
    """Save a new payment to database"""
    payment = Payment(**data)
    session.add(payment)
    await session.commit()
    await session.refresh(payment)
    return payment


async def update_payment_status(
    session: AsyncSession, 
    preference_id: str, 
    mp_payment_id: str, 
    status: str
):
    """Update payment status"""
    stmt = (
        update(Payment)
        .where(Payment.preference_id == preference_id)
        .values(status=status, mp_payment_id=mp_payment_id)
    )
    await session.execute(stmt)
    await session.commit()
    
    # Return updated payment
    result = await session.execute(
        select(Payment).where(Payment.preference_id == preference_id)
    )
    return result.scalar_one_or_none()


async def get_payment_by_id(session: AsyncSession, payment_id: str):
    """Get payment by ID"""
    result = await session.execute(
        select(Payment).where(Payment.id == uuid.UUID(payment_id))
    )
    return result.scalar_one_or_none()


async def get_payment_by_preference_id(session: AsyncSession, preference_id: str):
    """Get payment by preference ID"""
    result = await session.execute(
        select(Payment).where(Payment.preference_id == preference_id)
    )
    return result.scalar_one_or_none()
