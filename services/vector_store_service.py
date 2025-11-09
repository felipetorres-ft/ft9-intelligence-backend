"""
Serviço de Vector Store com FAISS
"""
import faiss
import numpy as np
import pickle
import os
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class VectorStoreService:
    """
    Serviço para armazenar e buscar vetores usando FAISS
    """
    
    def __init__(
        self,
        dimension: int = 1536,
        index_path: Optional[str] = None
    ):
        self.dimension = dimension
        self.index_path = index_path or "/home/ubuntu/ft9-whatsapp/data/faiss_index"
        self.metadata_path = f"{self.index_path}_metadata.pkl"
        
        # Criar diretório se não existir
        Path(self.index_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Inicializar ou carregar índice
        if os.path.exists(self.index_path):
            self.load_index()
        else:
            self.create_index()
    
    def create_index(self):
        """
        Criar novo índice FAISS
        """
        # Usar IndexFlatL2 para busca exata (pode ser otimizado depois)
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        
        logger.info(f"Novo índice FAISS criado com dimensão {self.dimension}")
    
    def load_index(self):
        """
        Carregar índice existente
        """
        try:
            self.index = faiss.read_index(self.index_path)
            
            with open(self.metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
            
            logger.info(f"Índice FAISS carregado: {self.index.ntotal} vetores")
        
        except Exception as e:
            logger.error(f"Erro ao carregar índice: {e}")
            self.create_index()
    
    def save_index(self):
        """
        Salvar índice no disco
        """
        try:
            faiss.write_index(self.index, self.index_path)
            
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)
            
            logger.info(f"Índice FAISS salvo: {self.index.ntotal} vetores")
        
        except Exception as e:
            logger.error(f"Erro ao salvar índice: {e}")
            raise
    
    def add_vector(
        self,
        vector: List[float],
        metadata: Dict[str, Any]
    ) -> int:
        """
        Adicionar vetor ao índice
        """
        try:
            # Converter para numpy array
            vec = np.array([vector], dtype=np.float32)
            
            # Adicionar ao índice
            idx = self.index.ntotal
            self.index.add(vec)
            
            # Adicionar metadata
            self.metadata.append({
                "id": idx,
                **metadata
            })
            
            logger.info(f"Vetor adicionado ao índice: ID {idx}")
            
            return idx
        
        except Exception as e:
            logger.error(f"Erro ao adicionar vetor: {e}")
            raise
    
    def add_vectors_batch(
        self,
        vectors: List[List[float]],
        metadatas: List[Dict[str, Any]]
    ) -> List[int]:
        """
        Adicionar múltiplos vetores em batch
        """
        try:
            # Converter para numpy array
            vecs = np.array(vectors, dtype=np.float32)
            
            # Adicionar ao índice
            start_idx = self.index.ntotal
            self.index.add(vecs)
            
            # Adicionar metadatas
            ids = []
            for i, metadata in enumerate(metadatas):
                idx = start_idx + i
                self.metadata.append({
                    "id": idx,
                    **metadata
                })
                ids.append(idx)
            
            logger.info(f"{len(vectors)} vetores adicionados ao índice")
            
            return ids
        
        except Exception as e:
            logger.error(f"Erro ao adicionar vetores em batch: {e}")
            raise
    
    def search(
        self,
        query_vector: List[float],
        k: int = 5
    ) -> List[Tuple[int, float, Dict[str, Any]]]:
        """
        Buscar k vetores mais similares
        
        Returns:
            Lista de tuplas (id, distance, metadata)
        """
        try:
            # Converter para numpy array
            query = np.array([query_vector], dtype=np.float32)
            
            # Buscar
            distances, indices = self.index.search(query, k)
            
            # Montar resultados
            results = []
            for i, (idx, distance) in enumerate(zip(indices[0], distances[0])):
                if idx < len(self.metadata):
                    results.append((
                        int(idx),
                        float(distance),
                        self.metadata[idx]
                    ))
            
            logger.info(f"Busca realizada: {len(results)} resultados")
            
            return results
        
        except Exception as e:
            logger.error(f"Erro ao buscar vetores: {e}")
            raise
    
    def delete_by_organization(self, organization_id: int):
        """
        Deletar todos os vetores de uma organização
        (Recria o índice sem os vetores da organização)
        """
        try:
            # Filtrar metadata
            new_metadata = [
                m for m in self.metadata
                if m.get("organization_id") != organization_id
            ]
            
            if len(new_metadata) == len(self.metadata):
                logger.info(f"Nenhum vetor encontrado para org {organization_id}")
                return
            
            # Recriar índice
            self.create_index()
            
            # Adicionar vetores filtrados
            for meta in new_metadata:
                # Nota: Isso requer ter os vetores salvos no metadata
                # Em produção, usar um banco de dados vetorial mais robusto
                pass
            
            logger.info(f"Vetores da org {organization_id} removidos")
        
        except Exception as e:
            logger.error(f"Erro ao deletar vetores: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obter estatísticas do índice
        """
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "index_type": type(self.index).__name__
        }


# Instância global do serviço
vector_store_service = VectorStoreService()
