"""
FT9 WhatsApp Integration - Main FastAPI Server
Direct integration with WhatsApp Business API - No Twilio, No Make
"""
import logging
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn

from config import settings
from whatsapp_client import whatsapp_client
from ai_processor import ai_processor
from session_manager import session_manager

# Importar Routers
from routers import knowledge_router_v2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="FT9 Intelligence Platform",
    description="Direct WhatsApp Business API integration with AI processing",
    version="2.0.0"
)

# Include routers
app.include_router(knowledge_router_v2.router, prefix="/api/v1/knowledge", tags=["knowledge"])


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
    return {
        "service": "FT9 Intelligence Platform",
        "version": "2.0.0",
        "status": "online",
        "features": [
            "Multi-Tenant Architecture",
            "WhatsApp Business API",
            "AI Processing with GPT-4.1",
            "JWT Authentication",
            "PostgreSQL Database",
            "Knowledge Base with RAG"
        ]
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
    """
    try:
        body = await request.json()
        logger.info(f"Received webhook: {body}")
        
        # Extract message data from WhatsApp webhook format
        if "entry" in body:
            for entry in body["entry"]:
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    
                    # Check if it's a message
                    if "messages" in value:
                        for message in value["messages"]:
                            await process_incoming_message(message, value)
        
        return JSONResponse(content={"status": "ok"}, status_code=200)
    
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return JSONResponse(content={"status": "error"}, status_code=500)


async def process_incoming_message(message: Dict[str, Any], value: Dict[str, Any]):
    """
    Process an incoming WhatsApp message
    
    Args:
        message: Message object from webhook
        value: Value object containing metadata
    """
    try:
        # Extract message details
        message_id = message.get("id")
        from_number = message.get("from")
        message_type = message.get("type")
        timestamp = message.get("timestamp")
        
        logger.info(f"Processing message {message_id} from {from_number}")
        
        # Handle text messages
        if message_type == "text":
            message_text = message.get("text", {}).get("body", "")
            
            # Mark message as read
            await whatsapp_client.mark_as_read(message_id)
            
            # Add user message to session
            session_manager.add_message(from_number, "user", message_text)
            
            # Get conversation history
            conversation_history = session_manager.get_conversation_history(
                from_number,
                limit=5  # Last 5 messages for context
            )
            
            # Process message with AI
            ai_response = await ai_processor.process_message(
                user_message=message_text,
                user_phone=from_number,
                conversation_history=conversation_history
            )
            
            # Add AI response to session
            session_manager.add_message(from_number, "assistant", ai_response)
            
            # Send response back to user
            await whatsapp_client.send_message(
                to=from_number,
                message=ai_response
            )
            
            logger.info(f"Response sent to {from_number}")
        
        else:
            logger.info(f"Unsupported message type: {message_type}")
            # Send a default response for unsupported types
            await whatsapp_client.send_message(
                to=from_number,
                message="Desculpe, no momento só consigo processar mensagens de texto. 📝"
            )
    
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
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


if __name__ == "__main__":
    logger.info(f"Starting FT9 WhatsApp Integration Server on {settings.host}:{settings.port}")
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development"
    )
