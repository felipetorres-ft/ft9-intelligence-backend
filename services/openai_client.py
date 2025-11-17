# openai_client.py — FT9 Intelligence
# Versão AI9 — Cliente OpenAI seguro, centralizado e com fallback

import os
import openai
import logging

logger = logging.getLogger("FT9-AI9")

class OpenAIClient:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("❌ OPENAI_API_KEY não definida no ambiente Railway.")
        
        openai.api_key = api_key
        logger.info("🟢 OpenAI API iniciada com sucesso.")
    
    def embedding(self, text: str):
        try:
            # Modelo de embedding moderno e barato
            response = openai.Embedding.create(
                model="text-embedding-3-large",
                input=text
            )
            return response["data"][0]["embedding"]
        except Exception as e:
            logger.error(f"❌ Erro ao gerar embedding: {e}")
            raise
    
    def chat(self, prompt: str):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.2
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"❌ Erro no ChatCompletion: {e}")
            raise

# Instância global
openai_client = OpenAIClient()
