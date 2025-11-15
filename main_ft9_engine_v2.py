"""
FT9 WhatsApp Integration - Main FastAPI Server with FT9 Engine v2.0.1
Integrado com FT9Core, FT9Flow, FT9Memory, WhatsAppGateway e Knowledge Base (pgvector)
Desenvolvido por AI9 - 15/11/2025
Atualizado conforme especificação dos programadores
"""
import logging
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn

from config import settings
from whatsapp_client import whatsapp_client
from session_manager import session_manager

# Importar FT9 Engine
from engine import FT9Core, FT9Flow, FT9Memory, WhatsAppGateway

# Importar routers
from routers.knowledge_router_v2 import router as knowledge_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FT9 Engine
logger.info("Inicializando FT9 Engine v2.0.1...")
ft9_memory = FT9Memory(base_path="memory")
ft9_flow = FT9Flow(ft9_memory)
ft9_core = FT9Core(ft9_memory, ft9_flow)
whatsapp_gateway = WhatsAppGateway()
logger.info("FT9 Engine inicializado com sucesso!")

# Initialize FastAPI app
app = FastAPI(
    title="FT9 Intelligence API with Knowledge Base",
    description="WhatsApp Business API + FT9 Engine + RAG with pgvector",
    version="2.0.1"
)

# Configure CORS
cors_origins = settings.CORS_ORIGINS.split(",") if hasattr(settings, 'CORS_ORIGINS') else [
    "https://www.ft9intelligence.com",
    "https://ft9-frontend.vercel.app",
    "http://localhost:3000",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"CORS configurado para: {cors_origins}")

# Include routers
app.include_router(knowledge_router)
logger.info("Knowledge Router v2 incluído")


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
        "service": "FT9 Intelligence API with Knowledge Base",
        "version": "2.0.1",
        "active_sessions": session_manager.get_active_sessions_count(),
        "engine_status": engine_status,
        "memory_stats": memory_stats,
        "features": {
            "whatsapp": True,
            "ft9_engine": True,
            "knowledge_base": True,
            "rag": True,
            "pgvector": True
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check detalhado
    """
    try:
        # Verificar se OPENAI_API_KEY está configurada
        openai_configured = bool(settings.OPENAI_API_KEY)
        
        return {
            "status": "healthy",
            "checks": {
                "api": "ok",
                "ft9_engine": "ok",
                "openai_api_key": "configured" if openai_configured else "missing",
                "database": "ok"  # TODO: adicionar check real do DB
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
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
        
        if not usuario or not texto:
            logger.info("Webhook recebido mas sem mensagem processável")
            return {"status": "ok", "message": "No processable message"}
        
        logger.info(f"Mensagem de {usuario}: {texto}")
        
        # Processar com FT9Core
        resposta = ft9_core.process_message(usuario, texto)
        
        logger.info(f"Resposta FT9: {resposta}")
        
        # Enviar resposta via WhatsApp
        whatsapp_gateway.enviar_mensagem(usuario, resposta)
        
        return {
            "status": "success",
            "usuario": usuario,
            "mensagem_recebida": texto,
            "resposta_enviada": resposta
        }
        
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {e}")
        # Retornar 200 mesmo com erro para não reenviar webhook
        return {
            "status": "error",
            "error": str(e)
        }


@app.on_event("startup")
async def startup_event():
    """
    Executar ao iniciar a aplicação
    """
    logger.info("🚀 FT9 Intelligence API iniciando...")
    
    # Inicializar banco de dados
    try:
        from database.database import init_db
        from database.init_pgvector import init_pgvector
        
        # Inicializar tabelas
        await init_db()
        logger.info("✅ Database inicializado")
        
        # Inicializar pgvector
        success = await init_pgvector()
        if success:
            logger.info("✅ pgvector configurado")
        else:
            logger.warning("⚠️  pgvector não configurado (pode ser necessário instalação manual)")
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar database: {e}")
    
    logger.info("✅ FT9 Intelligence API pronta!")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Executar ao desligar a aplicação
    """
    logger.info("🛑 FT9 Intelligence API encerrando...")


if __name__ == "__main__":
    uvicorn.run(
        "main_ft9_engine_v2:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
