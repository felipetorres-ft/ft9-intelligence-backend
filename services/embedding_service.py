# embedding_service.py — FT9 Intelligence
# Versão AI9 — Serviço dedicado para gerar embeddings

from services.openai_client import openai_client

async def generate_embedding(text: str):
    """
    Gera embedding usando OpenAI.
    Uso: dentro de rotas e serviços que precisam de vetores.
    """
    if not text or text.strip() == "":
        raise Exception("❌ Texto vazio recebido para embedding.")
    
    # Chamada síncrona porque OpenAI SDK não é async
    return openai_client.embedding(text)
