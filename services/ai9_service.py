"""
FT9 Intelligence - AI9 Service
Serviço de geração de respostas usando GPT-4o-mini (Camila)
"""

from openai import AsyncOpenAI
import os
import logging

logger = logging.getLogger(__name__)

# Cliente OpenAI (API key já configurada em variável de ambiente)
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def generate_ai9_response(mensagem: str, telefone: str) -> str:
    """
    Gera resposta da Camila (AI9) usando GPT-4o-mini
    
    Args:
        mensagem: Mensagem recebida do cliente
        telefone: Número de telefone do cliente (para contexto)
    
    Returns:
        Resposta gerada pela AI9
    """
    try:
        logger.info(f"[AI9] Gerando resposta para {telefone}: {mensagem[:50]}...")
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",    # Modelo correto
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
            max_tokens=500,         # Compatível com o SDK instalado
            temperature=0.7
        )
        
        ai_text = response.choices[0].message.content
        logger.info(f"[AI9] Resposta gerada: {ai_text[:100]}...")
        
        return ai_text
        
    except Exception as e:
        logger.error(f"[AI9] Erro ao gerar resposta: {e}")
        
        # Fallback seguro compatível com Z-API
        fallback_text = (
            "Olá! Aqui é a Camila da FT9 Intelligence. "
            "No momento estou com dificuldades técnicas para responder automaticamente, "
            "mas já estou resolvendo. Pode enviar sua dúvida que retornarei em seguida."
        )
        
        return fallback_text
