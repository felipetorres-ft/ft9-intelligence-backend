"""
FT9 WhatsApp Intelligence - Multi-Tenant Version
FastAPI server with database, authentication, and multi-tenant support
"""
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from config import settings
from database import init_db
from routers import auth_router, organization_router, billing_router, knowledge_router, automation_router

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle events - startup and shutdown
    """
    # Startup
    logger.info("Iniciando FT9 Intelligence Multi-Tenant...")
    logger.info(f"DATABASE_URL: {settings.DATABASE_URL}")
    
    try:
        # Inicializar banco de dados
        await init_db()
        logger.info("Banco de dados inicializado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {e}")
    
    yield
    
    # Shutdown
    logger.info("Encerrando FT9 Intelligence...")


# Criar aplicação FastAPI
app = FastAPI(
    title="FT9 Intelligence Platform",
    description="Plataforma Multi-Tenant de IA para WhatsApp Business",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth_router)
app.include_router(organization_router)
app.include_router(billing_router)
app.include_router(knowledge_router)
app.include_router(automation_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "FT9 Intelligence Platform",
        "version": "2.0.0",
        "status": "online",
        "features": [
            "Multi-Tenant Architecture",
            "WhatsApp Business API",
            "AI Processing with GPT-4.1",
            "JWT Authentication",
            "PostgreSQL Database"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "version": "2.0.0"
    }


@app.get("/webhook")
async def verify_webhook(request: Request):
    """
    Verificação do webhook pela Meta
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    if mode == "subscribe" and token == settings.WEBHOOK_VERIFY_TOKEN:
        logger.info("Webhook verificado com sucesso!")
        return int(challenge)
    else:
        logger.warning("Falha na verificação do webhook")
        raise HTTPException(status_code=403, detail="Forbidden")


@app.post("/webhook")
async def receive_webhook(request: Request):
    """
    Receber mensagens do WhatsApp
    TODO: Integrar com sistema multi-tenant
    """
    try:
        body = await request.json()
        logger.info(f"Webhook recebido: {body}")
        
        # TODO: Processar mensagem com contexto da organização
        # 1. Identificar organização pelo phone_number_id
        # 2. Buscar configurações da organização
        # 3. Processar mensagem com IA
        # 4. Salvar conversa e mensagem no banco
        # 5. Enviar resposta
        
        return JSONResponse(content={"status": "success"}, status_code=200)
    
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {str(e)}")
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=500
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level="info"
    )
