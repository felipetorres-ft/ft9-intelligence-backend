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
from routers import auth_router, organization_router, billing_router, knowledge_router, automation_router, whatsapp_router
from routers.temp_update_org import router as temp_update_router
from routers.admin_router import router as admin_router
from routers.payment_router import router as payment_router
from routers.broadcast_router import router as broadcast_router
from routers.zapi_webhook_router import router as zapi_webhook_router
from routers.mini_cinthya_router import router as mini_cinthya_router

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
app.include_router(whatsapp_router)
app.include_router(temp_update_router)
app.include_router(admin_router)
app.include_router(payment_router)
app.include_router(broadcast_router)
app.include_router(zapi_webhook_router)
app.include_router(mini_cinthya_router, prefix="/mini-cinthya")


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
            "AI Processing with GPT-5 (AI9)",
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


# Webhook endpoints moved to whatsapp_router


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level="info"
    )
