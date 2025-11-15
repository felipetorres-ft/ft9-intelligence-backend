# main.py — FT9 Intelligence Backend (Python 3.11)
# Versão AI9 — CORS Resolvido, Routers Carregados, Logs Ativados

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

# Routers
from routers.knowledge_router import router as knowledge_router

# ------------------------------------------------------
# LOGGING (IMPORTANTE PARA DIAGNÓSTICO NO RAILWAY)
# ------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------------------------------------------
# APLICAÇÃO FASTAPI
# ------------------------------------------------------
app = FastAPI(
    title="FT9 Intelligence Backend",
    version="1.0.0",
    description="Backend oficial do FT9 Intelligence mantido pela AI9"
)

# ------------------------------------------------------
# CORS — CONFIGURAÇÃO DEFINITIVA
# ------------------------------------------------------
origins = [
    "https://www.ft9intelligence.com",
    "https://ft9intelligence.com",
    "http://localhost:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Aceita os domínios oficiais
    allow_credentials=True,
    allow_methods=["*"],  # Libera todos os métodos
    allow_headers=["*"]  # Libera todos os headers
)

logger.info("🟢 CORS carregado com sucesso.")

# ------------------------------------------------------
# ROTAS
# ------------------------------------------------------
@app.get("/")
def root():
    return {"status": "OK", "message": "FT9 Backend online — versão AI9"}

app.include_router(knowledge_router, prefix="/api/v1")

# ------------------------------------------------------
# RODAR LOCALMENTE (Railway ignora)
# ------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
