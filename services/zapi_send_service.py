"""
FT9 Intelligence - Z-API Send Service
Serviço utilitário para envio de mensagens via Z-API
"""

import httpx
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Credenciais Z-API
ZAPI_INSTANCE_ID = os.getenv('ZAPI_INSTANCE_ID', '3EA61512E6CBA19EB3A9E243A9EE21C6')
ZAPI_TOKEN = os.getenv('ZAPI_TOKEN', '212CBB5256257083A240A4EC')
ZAPI_BASE_URL = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}"


async def enviar_msg(numero: str, texto: str) -> dict:
    """
    Envia mensagem de texto simples via Z-API
    
    Args:
        numero: Número WhatsApp com DDI+DDD (ex: 5511999999999)
        texto: Texto da mensagem
        
    Returns:
        dict: Response da Z-API
    """
    url = f"{ZAPI_BASE_URL}/send-text"

    payload = {
        "phone": numero,
        "message": texto  # ★ garantir que vem sem emojis proibidos
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:  # ★ timeout seguro
            response = await client.post(url, json=payload)
            
            if response.status_code != 200:
                logger.error(
                    f"❌ Falha Z-API {response.status_code}: {response.text}"
                )
            else:
                logger.info(f"Mensagem enviada para {numero}: {response.status_code}")
            
            return response.json()
    except Exception as e:
        logger.error(
            f"❌ Erro ao enviar Z-API: {e}"
        )
        return {"error": str(e)}


async def enviar_template(
    numero: str,
    template_id: str,
    variables: dict,
    buttons: Optional[list] = None
) -> dict:
    """
    Envia mensagem com template aprovado pela Meta
    
    Args:
        numero: Número WhatsApp com DDI+DDD
        template_id: ID do template aprovado na Meta
        variables: Variáveis do template (ex: {"nome": "João", "clinica": "ABC"})
        buttons: Lista de botões (opcional)
        
    Returns:
        dict: Response da Z-API
    """
    url = f"{ZAPI_BASE_URL}/send-template"
    
    payload = {
        "phone": numero,
        "templateId": template_id,
        "variables": variables
    }
    
    if buttons:
        payload["buttons"] = buttons

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json=payload)
            logger.info(f"Template enviado para {numero}: {response.status_code}")
            return response.json()
    except Exception as e:
        logger.error(f"Erro ao enviar template para {numero}: {e}")
        return {"error": str(e)}
