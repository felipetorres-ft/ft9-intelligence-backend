"""
Serviço de Embeddings para FT9-Memory
"""
from openai import OpenAI
from typing import List, Dict, Any, Optional
import numpy as np
import logging

logger = logging.getLogger(__name__)

client = OpenAI()


class EmbeddingService:
    """
    Serviço para gerar embeddings usando OpenAI
    """
    
    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model
        self.dimension = 1536  # Dimensão do modelo text-embedding-3-small
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Gerar embedding para um texto
        """
        try:
            response = client.embeddings.create(
                model=self.model,
                input=text
            )
            
            embedding = response.data[0].embedding
            logger.info(f"Embedding gerado para texto de {len(text)} caracteres")
            
            return embedding
        
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {e}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Gerar embeddings para múltiplos textos (batch)
        """
        try:
            response = client.embeddings.create(
                model=self.model,
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            logger.info(f"Embeddings gerados para {len(texts)} textos")
            
            return embeddings
        
        except Exception as e:
            logger.error(f"Erro ao gerar embeddings em batch: {e}")
            raise
    
    def cosine_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Calcular similaridade de cosseno entre dois embeddings
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        similarity = dot_product / (norm1 * norm2)
        
        return float(similarity)


# Instância global do serviço
embedding_service = EmbeddingService()
