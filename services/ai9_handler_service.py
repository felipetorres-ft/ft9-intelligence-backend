"""
FT9 Intelligence - AI9 Handler Service
Serviço para processar intenções de usuários via AI9
"""

import logging
from services.zapi_send_service import enviar_msg
from services.zoom_scheduler_service import agendar_zoom

logger = logging.getLogger(__name__)


async def process_user_intent(numero: str, texto: str, button_id: str = ""):
    """
    Processa a intenção do usuário e executa ação apropriada
    
    Args:
        numero: Número WhatsApp do usuário
        texto: Texto da mensagem (se houver)
        button_id: ID do botão clicado (se houver)
    """
    logger.info(f"🤖 Processando intenção de {numero}")
    logger.info(f"   Texto: {texto}")
    logger.info(f"   Botão: {button_id}")
    
    # Processar clique em botões
    if button_id == "btn_agendar":
        logger.info(f"📅 {numero} quer agendar reunião")
        await agendar_zoom(numero)
        return

    if button_id == "btn_info":
        logger.info(f"ℹ️ {numero} quer mais informações")
        await enviar_msg(
            numero,
            "Claro! O que você gostaria de saber sobre a FT9 Intelligence? "
            "Estou aqui para ajudar! 😊"
        )
        return

    if button_id == "btn_parar":
        logger.info(f"🛑 {numero} pediu para parar envios")
        await enviar_msg(
            numero,
            "Prontinho! Você não receberá mais mensagens. "
            "Se mudar de ideia, é só entrar em contato! 👍"
        )
        # TODO: Adicionar número à lista de opt-out
        return

    # Processar mensagem de texto natural
    if texto:
        logger.info(f"💬 Processando mensagem de texto natural")
        
        # TODO: Integrar com AI9 (GPT) para resposta inteligente
        # Por enquanto, resposta padrão
        await enviar_msg(
            numero,
            "Olá! Aqui é o atendimento da FT9 Intelligence. "
            "Como posso ajudar você hoje? 😊"
        )
        return

    # Caso não tenha texto nem botão
    logger.warning(f"⚠️ Evento sem texto ou botão de {numero}")
