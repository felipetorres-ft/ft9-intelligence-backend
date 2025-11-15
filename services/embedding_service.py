"""
Serviço de geração de embeddings usando OpenAI
Versão final – AI9
"""

import os
import logging
import requests
from typing import List, Optional
import numpy as np
from config import settings

logger = logging.getLogger("FT9-EmbeddingService")


class EmbeddingService:
    """
    Serviço para gerar embeddings vetoriais usando OpenAI API
    Modelo: text-embedding-ada-002 (1536 dimensões)
    """

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = "text-embedding-ada-002"
        self.api_url = "https://api.openai.com/v1/embeddings"
        self.dimensions = 1536

        if not self.api_key:
            logger.warning("⚠️ OPENAI_API_KEY não configurada. Embeddings não funcionarão.")

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Gerar embedding para um texto"""
        if not self.api_key:
            logger.error("❌ OPENAI_API_KEY não configurada")
            return None

        if not text or not text.strip():
            logger.error("❌ Texto vazio fornecido")
            return None

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "model": self.model,
                "input": text.strip(),
            }

            logger.info(f"🔄 Gerando embedding ({len(text)} chars)...")

            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30,
            )

            response.raise_for_status()
            data = response.json()
            embedding = data["data"][0]["embedding"]

            return embedding

        except Exception as e:
            logger.error(f"❌ Erro ao gerar embedding: {e}")
            return None


# Instância global – ESSENCIAL para não quebrar imports
embedding_service = EmbeddingService()


# Função auxiliar de compatibilidade
def generate_embedding(text: str):
    return embedding_service.generate_embedding(text)
