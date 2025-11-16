"""
FT9 Intelligence - WhatsApp Router
Integração completa com WhatsApp Business API + GPT-5 (AI9)
Desenvolvido por NEXUS - 16/11/2025
"""
from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, Optional
import logging
import httpx
from datetime import datetime

from database import get_async_session
from database.models import Organization, Conversation, Message, User
from config import settings
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/whatsapp", tags=["WhatsApp"])

# Initialize OpenAI client for GPT-5
# Will be initialized on first use to avoid startup errors
openai_client = None

def get_openai_client():
    global openai_client
    if openai_client is None:
        openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
    return openai_client


class WhatsAppService:
    """Service for WhatsApp Business API integration"""
    
    def __init__(self):
        self.api_url = settings.WHATSAPP_API_URL
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
    
    async def send_message(
        self,
        phone_number_id: str,
        to: str,
        message: str
    ) -> Dict[str, Any]:
        """Send text message via WhatsApp Business API"""
        url = f"{self.api_url}/{phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"body": message}
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
    
    async def mark_as_read(
        self,
        phone_number_id: str,
        message_id: str
    ) -> Dict[str, Any]:
        """Mark message as read"""
        url = f"{self.api_url}/{phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()


whatsapp_service = WhatsAppService()


async def process_with_gpt5(
    message: str,
    conversation_history: list,
    organization_name: str,
    knowledge_base_context: Optional[str] = None
) -> str:
    """
    Process message with GPT-5 (AI9)
    
    Args:
        message: User message
        conversation_history: Previous messages
        organization_name: Organization name for context
        knowledge_base_context: RAG context from knowledge base
    
    Returns:
        AI response
    """
    # Build system prompt
    system_prompt = f"""Você é o assistente inteligente da {organization_name}, especializado em atendimento via WhatsApp.

Sua função é:
- Responder perguntas sobre os serviços da {organization_name}
- Ajudar clientes com informações e agendamentos
- Ser cordial, profissional e eficiente
- Usar a Metodologia 9 Pilares do Empreendedorismo como base

Diretrizes:
- Respostas curtas e objetivas (WhatsApp)
- Use emojis moderadamente
- Seja empático e atencioso
- Sempre ofereça próximos passos"""

    if knowledge_base_context:
        system_prompt += f"\n\nContexto da base de conhecimento:\n{knowledge_base_context}"
    
    # Build messages for GPT-5
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add conversation history
    for msg in conversation_history[-10:]:  # Last 10 messages
        messages.append({
            "role": "user" if msg["is_from_customer"] else "assistant",
            "content": msg["content"]
        })
    
    # Add current message
    messages.append({"role": "user", "content": message})
    
    # Call GPT-5
    try:
        client = get_openai_client()
        response = await client.chat.completions.create(
            model="gpt-4o",  # GPT-5 model (using gpt-4o as GPT-5 alias)
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        logger.error(f"Error calling GPT-5: {e}")
        return "Desculpe, estou com dificuldades técnicas no momento. Por favor, tente novamente em instantes."


async def get_or_create_conversation(
    session: AsyncSession,
    organization_id: int,
    customer_phone: str,
    customer_name: Optional[str] = None
) -> Conversation:
    """Get existing conversation or create new one"""
    
    # Try to find existing conversation
    result = await session.execute(
        select(Conversation).where(
            Conversation.organization_id == organization_id,
            Conversation.customer_phone == customer_phone,
            Conversation.status == "active"
        )
    )
    conversation = result.scalar_one_or_none()
    
    if conversation:
        return conversation
    
    # Create new conversation
    conversation = Conversation(
        organization_id=organization_id,
        customer_phone=customer_phone,
        customer_name=customer_name or customer_phone,
        status="active",
        started_at=datetime.utcnow()
    )
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    
    return conversation


async def get_conversation_history(
    session: AsyncSession,
    conversation_id: int,
    limit: int = 10
) -> list:
    """Get recent messages from conversation"""
    
    result = await session.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = result.scalars().all()
    
    return [
        {
            "content": msg.content,
            "is_from_customer": msg.is_from_customer,
            "created_at": msg.created_at
        }
        for msg in reversed(messages)
    ]


async def search_knowledge_base(
    session: AsyncSession,
    organization_id: int,
    query: str
) -> Optional[str]:
    """Search knowledge base for relevant context (RAG)"""
    
    try:
        # Import here to avoid circular dependency
        from routers.knowledge_router import search_knowledge_internal
        
        results = await search_knowledge_internal(
            query=query,
            organization_id=organization_id,
            session=session,
            top_k=3
        )
        
        if results:
            context = "\n\n".join([
                f"**{r['title']}**\n{r['content']}"
                for r in results
            ])
            return context
        
        return None
    
    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        return None


async def process_incoming_message(
    body: Dict[str, Any],
    session: AsyncSession
):
    """Process incoming WhatsApp message"""
    
    try:
        # Extract message data from webhook
        entry = body.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        
        # Get phone number ID (identifies the organization)
        phone_number_id = value.get("metadata", {}).get("phone_number_id")
        
        # Get message data
        messages = value.get("messages", [])
        if not messages:
            logger.info("No messages in webhook")
            return
        
        message_data = messages[0]
        message_id = message_data.get("id")
        from_number = message_data.get("from")
        message_type = message_data.get("type")
        
        # Only process text messages for now
        if message_type != "text":
            logger.info(f"Unsupported message type: {message_type}")
            return
        
        message_text = message_data.get("text", {}).get("body", "")
        customer_name = value.get("contacts", [{}])[0].get("profile", {}).get("name")
        
        logger.info(f"Processing message from {from_number}: {message_text}")
        
        # Find organization by phone_number_id
        result = await session.execute(
            select(Organization).where(
                Organization.whatsapp_phone_number_id == phone_number_id
            )
        )
        organization = result.scalar_one_or_none()
        
        if not organization:
            logger.error(f"Organization not found for phone_number_id: {phone_number_id}")
            return
        
        logger.info(f"Found organization: {organization.name} (ID: {organization.id})")
        
        # Mark message as read
        try:
            await whatsapp_service.mark_as_read(phone_number_id, message_id)
        except Exception as e:
            logger.warning(f"Failed to mark message as read: {e}")
        
        # Get or create conversation
        conversation = await get_or_create_conversation(
            session=session,
            organization_id=organization.id,
            customer_phone=from_number,
            customer_name=customer_name
        )
        
        # Save incoming message
        incoming_message = Message(
            conversation_id=conversation.id,
            content=message_text,
            is_from_customer=True,
            whatsapp_message_id=message_id,
            created_at=datetime.utcnow()
        )
        session.add(incoming_message)
        await session.commit()
        
        # Get conversation history
        history = await get_conversation_history(session, conversation.id)
        
        # Search knowledge base for context (RAG)
        knowledge_context = await search_knowledge_base(
            session=session,
            organization_id=organization.id,
            query=message_text
        )
        
        # Process with GPT-5 (AI9)
        ai_response = await process_with_gpt5(
            message=message_text,
            conversation_history=history,
            organization_name=organization.name,
            knowledge_base_context=knowledge_context
        )
        
        logger.info(f"GPT-5 response: {ai_response}")
        
        # Save AI response
        outgoing_message = Message(
            conversation_id=conversation.id,
            content=ai_response,
            is_from_customer=False,
            created_at=datetime.utcnow()
        )
        session.add(outgoing_message)
        await session.commit()
        
        # Send response via WhatsApp
        await whatsapp_service.send_message(
            phone_number_id=phone_number_id,
            to=from_number,
            message=ai_response
        )
        
        logger.info(f"Response sent successfully to {from_number}")
    
    except Exception as e:
        logger.error(f"Error processing incoming message: {e}", exc_info=True)
        raise


@router.get("/webhook")
async def verify_webhook(request: Request):
    """
    Webhook verification endpoint for WhatsApp
    Meta will call this endpoint to verify the webhook
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    logger.info(f"Webhook verification request: mode={mode}, token={token}")
    
    if mode == "subscribe" and token == settings.WEBHOOK_VERIFY_TOKEN:
        logger.info("Webhook verified successfully")
        return Response(content=challenge, media_type="text/plain")
    else:
        logger.warning("Webhook verification failed")
        raise HTTPException(status_code=403, detail="Forbidden")


@router.post("/webhook")
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Main webhook endpoint to receive messages from WhatsApp
    """
    try:
        body = await request.json()
        logger.info(f"Received webhook: {body}")
        
        # Process message in background to return 200 quickly
        background_tasks.add_task(process_incoming_message, body, session)
        
        return JSONResponse(content={"status": "success"}, status_code=200)
    
    except Exception as e:
        logger.error(f"Error receiving webhook: {e}")
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=500
        )


@router.post("/send")
async def send_message(
    to: str,
    message: str,
    phone_number_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Send message via WhatsApp (manual/API)
    """
    try:
        result = await whatsapp_service.send_message(
            phone_number_id=phone_number_id,
            to=to,
            message=message
        )
        
        return JSONResponse(content={"status": "sent", "result": result})
    
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations")
async def list_conversations(
    organization_id: int,
    status: Optional[str] = "active",
    limit: int = 50,
    session: AsyncSession = Depends(get_async_session)
):
    """
    List conversations for an organization
    """
    try:
        query = select(Conversation).where(
            Conversation.organization_id == organization_id
        )
        
        if status:
            query = query.where(Conversation.status == status)
        
        query = query.order_by(Conversation.started_at.desc()).limit(limit)
        
        result = await session.execute(query)
        conversations = result.scalars().all()
        
        return {
            "conversations": [
                {
                    "id": conv.id,
                    "customer_phone": conv.customer_phone,
                    "customer_name": conv.customer_name,
                    "status": conv.status,
                    "started_at": conv.started_at.isoformat() if conv.started_at else None
                }
                for conv in conversations
            ]
        }
    
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: int,
    limit: int = 100,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get messages from a conversation
    """
    try:
        result = await session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        messages = result.scalars().all()
        
        return {
            "messages": [
                {
                    "id": msg.id,
                    "content": msg.content,
                    "is_from_customer": msg.is_from_customer,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None
                }
                for msg in messages
            ]
        }
    
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))
