"""
FT9 Intelligence - Z-API Webhook Router
Recebe e processa webhooks da Z-API (incluindo respostas automáticas AI9)
"""

from fastapi import APIRouter, Request
import logging
from services.ai9_service import generate_ai9_response
from services.zapi_send_service import enviar_msg

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/zapi/webhook", tags=["ZAPI Webhook"])


@router.get("/")
async def webhook_info():
    """
    Endpoint de informação do webhook (para testes)
    """
    return {
        "status": "active",
        "message": "FT9 Z-API Webhook is running",
        "version": "2.0.0 (AI9 Enabled)",
        "endpoints": {
            "POST /zapi/webhook/": "Receive Z-API webhooks"
        },
        "features": [
            "ReceivedCallback → AI9 auto-reply",
            "DeliveryCallback → Delivery tracking",
            "MessageStatusCallback → Status tracking"
        ]
    }


@router.post("/")
async def zapi_webhook(request: Request):
    """
    Recebe webhooks da Z-API e processa eventos
    
    Tipos de eventos suportados:
    - ReceivedCallback: Mensagem recebida do cliente → Gera resposta AI9
    - DeliveryCallback: Confirmação de entrega
    - MessageStatusCallback: Status da mensagem (SENT, RECEIVED, READ)
    
    Formatos suportados:
    1. Formato Z-API padrão (ReceivedCallback):
       {"phone": "...", "text": {"message": "..."}, "type": "ReceivedCallback"}
    
    2. Formato legado (compatibilidade):
       {"message": {"phone": "...", "text": "..."}}
    """
    try:
        data = await request.json()
        logger.info(f"📨 Webhook recebido: {data}")
        
        event_type = data.get("type")
        
        # ===============================
        # FORMATO 1: Z-API PADRÃO (ReceivedCallback)
        # ===============================
        if event_type == "ReceivedCallback":
            phone = data.get("phone")
            text_obj = data.get("text") or {}
            message = text_obj.get("message")
            
            # Validação de dados
            if not phone:
                logger.warning("⚠️ Webhook sem número de telefone")
                return {"status": "ok", "message": "Número não fornecido"}
            
            if not message:
                logger.warning(f"⚠️ Webhook sem mensagem de texto para {phone}")
                return {"status": "ok", "message": "Mensagem vazia"}
            
            logger.info(f"💬 Mensagem recebida de {phone}: {message}")
            
            # 2) Gera resposta usando AI9 (GPT-5.1 - Camila)
            try:
                resposta = await generate_ai9_response(message, phone)
                logger.info(f"🤖 AI9 gerou resposta: {resposta[:100]}...")
            except Exception as e:
                logger.error(f"❌ Erro ao gerar resposta AI9: {str(e)}")
                return {"status": "error", "message": "Erro ao gerar resposta AI9"}
            
            # 3) Envia a resposta via Z-API
            try:
                await enviar_msg(phone, resposta)
                logger.info(f"✅ Resposta enviada para {phone}")
            except Exception as e:
                logger.error(f"❌ Erro ao enviar resposta para {phone}: {str(e)}")
                return {"status": "error", "message": "Erro ao enviar resposta"}
            
            return {
                "status": "ok",
                "message": "AI9 respondeu com sucesso",
                "phone": phone,
                "response_preview": resposta[:50] + "..."
            }
        
        # ===============================
        # FORMATO 2: LEGADO (compatibilidade)
        # ===============================
        elif "message" in data and isinstance(data["message"], dict):
            message_obj = data.get("message", {})
            phone = message_obj.get("phone")
            text = message_obj.get("text")
            
            if not phone:
                logger.warning("⚠️ Webhook legado sem número de telefone")
                return {"status": "ok", "message": "Número não fornecido"}
            
            if not text:
                logger.warning(f"⚠️ Webhook legado sem texto para {phone}")
                return {"status": "ok", "message": "Mensagem vazia"}
            
            logger.info(f"💬 Mensagem recebida (formato legado) de {phone}: {text}")
            
            # Gera resposta AI9
            try:
                resposta = await generate_ai9_response(text, phone)
                logger.info(f"🤖 AI9 gerou resposta: {resposta[:100]}...")
            except Exception as e:
                logger.error(f"❌ Erro ao gerar resposta AI9: {str(e)}")
                return {"status": "error", "message": "Erro ao gerar resposta AI9"}
            
            # Envia resposta
            try:
                await enviar_msg(phone, resposta)
                logger.info(f"✅ Resposta enviada para {phone}")
            except Exception as e:
                logger.error(f"❌ Erro ao enviar resposta para {phone}: {str(e)}")
                return {"status": "error", "message": "Erro ao enviar resposta"}
            
            return {
                "status": "ok",
                "message": "AI9 respondeu com sucesso (formato legado)",
                "phone": phone,
                "response_preview": resposta[:50] + "..."
            }
        
        # ===============================
        # DELIVERY CALLBACK
        # ===============================
        elif event_type == "DeliveryCallback":
            phone = data.get("phone")
            message_id = data.get("messageId")
            error = data.get("error")
            
            if error:
                logger.warning(f"⚠️ Erro na entrega para {phone}: {error}")
            else:
                logger.info(f"✅ Mensagem entregue para {phone} (ID: {message_id})")
            
            return {"status": "ok", "message": "Delivery callback processado"}
        
        # ===============================
        # MESSAGE STATUS CALLBACK
        # ===============================
        elif event_type == "MessageStatusCallback":
            phone = data.get("phone")
            status = data.get("status")
            message_ids = data.get("ids", [])
            
            logger.info(f"📊 Status da mensagem: {status} | {phone} | IDs: {message_ids}")
            
            return {"status": "ok", "message": "Status callback processado"}
        
        # ===============================
        # OUTROS EVENTOS
        # ===============================
        else:
            logger.info(f"ℹ️ Tipo de evento ignorado: {event_type}")
            return {"status": "ok", "message": "Evento ignorado"}
    
    except Exception as e:
        logger.error(f"❌ Erro ao processar webhook: {str(e)}", exc_info=True)
        # Retornar 200 mesmo com erro para evitar retry do Z-API
        return {"status": "error", "message": str(e)}
