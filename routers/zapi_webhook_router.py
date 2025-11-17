"""
FT9 Intelligence - Z-API Webhook Router
Endpoints para receber webhooks do Z-API
"""

from fastapi import APIRouter, Request
import logging

from services.ai9_handler_service import process_user_intent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/zapi/webhook", tags=["ZAPI Webhook"])


@router.post("/")
async def receive_webhook(request: Request):
    """
    Recebe webhooks do Z-API com mensagens e eventos
    
    **Autenticação:** Não requerida (webhook público)
    
    **Payload Exemplo:**
    ```json
    {
      "message": {
        "phone": "5511999999999",
        "text": "Olá, quero mais informações",
        "button": "btn_info"
      }
    }
    ```
    
    **Eventos Processados:**
    - Mensagens de texto
    - Cliques em botões
    - Respostas a templates
    
    **Ações:**
    - btn_agendar → Scheduler Zoom
    - btn_info → AI9 responde
    - btn_parar → Opt-out automático
    - Texto natural → AI9 processa
    
    **Configuração no Z-API:**
    URL: https://ft9-intelligence-backend-production.up.railway.app/zapi/webhook/
    """
    try:
        payload = await request.json()
        logger.info(f"📨 Webhook recebido: {payload}")

        # Extrair dados da mensagem
        message = payload.get("message", {})
        numero = message.get("phone", "")
        texto = message.get("text", "")
        button_id = message.get("button", "")

        # Validar dados mínimos
        if not numero:
            logger.warning("⚠️ Webhook sem número de telefone")
            return {"status": "ok", "message": "Número não fornecido"}

        # Processar intenção via AI9
        await process_user_intent(numero, texto, button_id)

        return {"status": "ok", "message": "Webhook processado com sucesso"}

    except Exception as e:
        logger.error(f"❌ Erro ao processar webhook: {e}")
        # Retornar 200 mesmo com erro para evitar retry do Z-API
        return {"status": "error", "message": str(e)}


@router.get("/")
async def webhook_info():
    """
    Informações sobre o webhook (para testes)
    """
    return {
        "service": "FT9 Intelligence - Z-API Webhook",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "POST /zapi/webhook/": "Receber webhooks do Z-API"
        },
        "configuration": {
            "url": "https://ft9-intelligence-backend-production.up.railway.app/zapi/webhook/",
            "method": "POST",
            "content_type": "application/json"
        }
    }
