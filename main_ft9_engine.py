"""
FT9 WhatsApp Integration - Main FastAPI Server with FT9 Engine
Integrado com FT9Core, FT9Flow, FT9Memory e WhatsAppGateway
Desenvolvido por AI9 - 13/11/2025
"""
import logging
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn

from config import settings
from whatsapp_client import whatsapp_client
from session_manager import session_manager

# Importar FT9 Engine
from engine import FT9Core, FT9Flow, FT9Memory, WhatsAppGateway

# Importar Routers
from routers import funnel, dashboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FT9 Engine
logger.info("Inicializando FT9 Engine...")
ft9_memory = FT9Memory(base_path="memory")
ft9_flow = FT9Flow(ft9_memory)
ft9_core = FT9Core(ft9_memory, ft9_flow)
whatsapp_gateway = WhatsAppGateway()
logger.info("FT9 Engine inicializado com sucesso!")

# Initialize FastAPI app
app = FastAPI(
    title="FT9 WhatsApp Integration with AI9 Engine",
    description="Direct WhatsApp Business API integration with FT9 Intelligence Engine",
    version="2.0.0"
)

# Include routers
app.include_router(funnel.router, prefix="/funnel", tags=["funnel"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])


# Pydantic models for request validation
class WebhookMessage(BaseModel):
    """Model for incoming webhook messages"""
    from_number: str
    message_text: str
    message_id: str
    timestamp: str


@app.get("/")
async def root():
    """Health check endpoint"""
    engine_status = ft9_core.get_status()
    memory_stats = ft9_memory.get_stats()
    
    return {
        "status": "online",
        "service": "FT9 WhatsApp Integration with AI9 Engine",
        "version": "2.0.0",
        "active_sessions": session_manager.get_active_sessions_count(),
        "engine_status": engine_status,
        "memory_stats": memory_stats
    }


@app.get("/webhook")
async def verify_webhook(request: Request):
    """
    Webhook verification endpoint for WhatsApp
    Meta will call this endpoint to verify the webhook
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    logger.info(f"Webhook verification request: mode={mode}, token={token}")
    
    if mode == "subscribe" and token == settings.whatsapp_verify_token:
        logger.info("Webhook verified successfully")
        return Response(content=challenge, media_type="text/plain")
    else:
        logger.warning("Webhook verification failed")
        raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/webhook")
async def receive_webhook(request: Request):
    """
    Main webhook endpoint to receive messages from WhatsApp
    Integrado com WhatsAppGateway e FT9Core
    """
    try:
        body = await request.json()
        logger.info(f"Received webhook: {body}")
        
        # Usar WhatsAppGateway para processar evento
        usuario, texto = whatsapp_gateway.processar_evento(body)
        
        if usuario and texto:
            await process_incoming_message_ft9(usuario, texto, body)
        
        return JSONResponse(content={"status": "ok"}, status_code=200)
    
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return JSONResponse(content={"status": "error"}, status_code=500)


async def process_incoming_message_ft9(
    from_number: str,
    message_text: str,
    webhook_body: Dict[str, Any]
):
    """
    Processa mensagem usando FT9 Engine
    
    Args:
        from_number: Número do remetente
        message_text: Texto da mensagem
        webhook_body: Corpo completo do webhook
    """
    try:
        logger.info(f"Processing message from {from_number} with FT9 Engine")
        
        # Extrair message_id do webhook
        message_id = None
        if "entry" in webhook_body:
            for entry in webhook_body["entry"]:
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    if "messages" in value:
                        for message in value["messages"]:
                            message_id = message.get("id")
                            break
        
        # Mark message as read
        if message_id:
            await whatsapp_client.mark_as_read(message_id)
        
        # Add user message to session
        session_manager.add_message(from_number, "user", message_text)
        
        # Get conversation history
        conversation_history = session_manager.get_conversation_history(
            from_number,
            limit=5  # Last 5 messages for context
        )
        
        # Processar com FT9Core
        contexto = {
            "historico": conversation_history,
            "webhook_body": webhook_body
        }
        
        ai_response = ft9_core.processar(
            mensagem=message_text,
            usuario=from_number,
            contexto=contexto
        )
        
        # Add AI response to session
        session_manager.add_message(from_number, "assistant", ai_response)
        
        # Send response back to user
        await whatsapp_client.send_message(
            to=from_number,
            message=ai_response
        )
        
        logger.info(f"Response sent to {from_number} via FT9 Engine")
    
    except Exception as e:
        logger.error(f"Error processing message with FT9 Engine: {str(e)}")
        # Send error message to user
        try:
            await whatsapp_client.send_message(
                to=from_number,
                message="Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente."
            )
        except:
            pass


@app.post("/send-message")
async def send_message_endpoint(
    to: str,
    message: str
):
    """
    Manual endpoint to send messages (for testing or admin use)
    
    Args:
        to: Phone number to send to
        message: Message text
    """
    try:
        result = await whatsapp_client.send_message(to, message)
        return JSONResponse(content={"status": "sent", "result": result})
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions")
async def get_sessions():
    """Get information about active sessions"""
    return {
        "active_sessions": session_manager.get_active_sessions_count(),
        "session_timeout_minutes": 30
    }


@app.delete("/sessions/{phone_number}")
async def clear_session(phone_number: str):
    """Clear a specific user's session"""
    session_manager.clear_session(phone_number)
    return {"status": "cleared", "phone_number": phone_number}


@app.get("/engine/status")
async def get_engine_status():
    """Get FT9 Engine status"""
    return {
        "core": ft9_core.get_status(),
        "memory": ft9_memory.get_stats()
    }


@app.get("/personas")
async def list_personas():
    """List all loaded personas"""
    personas = ft9_memory.list_personas()
    return {
        "count": len(personas),
        "personas": list(personas.keys())
    }


@app.get("/personas/{user_id}")
async def get_persona(user_id: str):
    """Get specific persona"""
    persona = ft9_memory.get_persona(user_id)
    if persona:
        return persona
    else:
        raise HTTPException(status_code=404, detail="Persona not found")


if __name__ == "__main__":
    logger.info(f"Starting FT9 WhatsApp Integration with AI9 Engine on {settings.host}:{settings.port}")
    uvicorn.run(
        "main_ft9_engine:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development"
    )
