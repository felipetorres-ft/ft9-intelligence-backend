"""
FT9 Intelligence - AI9 Service
Serviço de geração de respostas usando GPT-5.1 (Camila)
"""

from openai import AsyncOpenAI
import os
import logging

logger = logging.getLogger(__name__)

# Cliente OpenAI (API key já configurada em variável de ambiente)
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def generate_ai9_response(mensagem: str, telefone: str) -> str:
    """
    Gera resposta da Camila (AI9) usando GPT-5.1
    
    Args:
        mensagem: Mensagem recebida do cliente
        telefone: Número de telefone do cliente (para contexto)
    
    Returns:
        Resposta gerada pela AI9
    """
    try:
        logger.info(f"[AI9] Gerando resposta para {telefone}: {mensagem[:50]}...")
        
        completion = await client.chat.completions.create(
            model="gpt-5.1",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é Camila, atendente virtual da FT9 Intelligence. "
                        "Você é profissional, clara, acolhedora e objetiva. "
                        "Seu objetivo principal é agendar a mentoria de 2 horas com Felipe Torres. "
                        "Seja cordial, mas direta. Evite respostas muito longas. "
                        "Se o cliente perguntar sobre preços, diga que a mentoria é personalizada "
                        "e que você pode agendar uma conversa para entender melhor as necessidades dele."
                    )
                },
                {
                    "role": "user",
                    "content": mensagem
                }
            ],
            temperature=0.7,
            max_completion_tokens=500  # ★ CORREÇÃO CRÍTICA: substituir max_tokens
        )
        
        resposta = completion.choices[0].message.content.strip()
        logger.info(f"[AI9] Resposta gerada: {resposta[:100]}...")
        
        return resposta
        
    except Exception as e:
        logger.error(f"[AI9] Erro ao gerar resposta: {str(e)}")
        # Resposta de fallback em caso de erro
        # ★ NOVO FALLBACK 100% COMPATÍVEL COM Z-API (sem emojis, sem unicode proibido)
        fallback_text = (
            "Olá! Aqui é a Camila da FT9 Intelligence. "
            "No momento estou com dificuldades técnicas para responder automaticamente, "
            "mas já estou resolvendo. Pode enviar sua dúvida que retornarei em seguida."
        )
        
        return fallback_text
