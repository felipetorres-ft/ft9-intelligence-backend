"""
Serviço de geração de embeddings usando OpenAI
Implementado conforme especificação dos programadores - 15/11/2025
Usa requests HTTP direto (não biblioteca openai) para maior controle
"""
import os
import logging
import requests
from typing import List, Optional
import numpy as np
from config import settings

logger = logging.getLogger(__name__)


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
            logger.warning("⚠️  OPENAI_API_KEY não configurada. Embeddings não funcionarão.")
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Gerar embedding para um texto
        
        Args:
            text: Texto para gerar embedding
            
        Returns:
            Lista de floats (1536 dimensões) ou None em caso de erro
        """
        if not self.api_key:
            logger.error("❌ OPENAI_API_KEY não configurada")
            return None
        
        if not text or not text.strip():
            logger.error("❌ Texto vazio fornecido")
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "input": text.strip()
            }
            
            logger.info(f"🔄 Gerando embedding para texto ({len(text)} caracteres)...")
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            
            data = response.json()
            embedding = data["data"][0]["embedding"]
            
            logger.info(f"✅ Embedding gerado com sucesso ({len(embedding)} dimensões)")
            
            return embedding
            
        except requests.exceptions.Timeout:
            logger.error("❌ Timeout ao gerar embedding")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erro na requisição OpenAI: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Resposta: {e.response.text}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro inesperado ao gerar embedding: {e}")
            return None
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Gerar embeddings para múltiplos textos
        
        Args:
            texts: Lista de textos
            
        Returns:
            Lista de embeddings (pode conter None para textos que falharam)
        """
        if not self.api_key:
            logger.error("❌ OPENAI_API_KEY não configurada")
            return [None] * len(texts)
        
        embeddings = []
        
        for i, text in enumerate(texts):
            logger.info(f"📝 Processando texto {i+1}/{len(texts)}...")
            embedding = self.generate_embedding(text)
            embeddings.append(embedding)
        
        success_count = sum(1 for e in embeddings if e is not None)
        logger.info(f"✅ {success_count}/{len(texts)} embeddings gerados com sucesso")
        
        return embeddings
    
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
    
    def validate_embedding(self, embedding: List[float]) -> bool:
        """
        Validar se um embedding está no formato correto
        
        Args:
            embedding: Lista de floats
            
        Returns:
            True se válido, False caso contrário
        """
        if not embedding:
            return False
        
        if not isinstance(embedding, list):
            return False
        
        if len(embedding) != self.dimensions:
            logger.error(f"❌ Embedding com dimensões incorretas: {len(embedding)} (esperado: {self.dimensions})")
            return False
        
        if not all(isinstance(x, (int, float)) for x in embedding):
            logger.error("❌ Embedding contém valores não numéricos")
            return False
        
        return True


# Instância global do serviço
embedding_service = EmbeddingService()


# Função auxiliar para compatibilidade com código legado
def generate_embedding(text: str) -> Optional[List[float]]:
    """
    Função auxiliar para gerar embedding (compatibilidade)
    """
    return embedding_service.generate_embedding(text)
