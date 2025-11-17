"""
Serviço RAG (Retrieval-Augmented Generation)
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import KnowledgeBase
from services.embedding_service import embedding_service
from services.vector_store_service import vector_store_service
from openai import OpenAI
import logging
import json

logger = logging.getLogger(__name__)

client = OpenAI()


class RAGService:
    """
    Serviço para Retrieval-Augmented Generation
    """
    
    def __init__(self, top_k: int = 3):
        self.top_k = top_k
    
    async def add_knowledge(
        self,
        db: AsyncSession,
        organization_id: int,
        title: str,
        content: str,
        source: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Adicionar conhecimento à base
        """
        try:
            # Gerar embedding
            embedding = embedding_service.generate_embedding(content)
            
            # Salvar no banco de dados
            knowledge = KnowledgeBase(
                organization_id=organization_id,
                title=title,
                content=content,
                source=source,
                category=category,
                tags=json.dumps(tags) if tags else None,
                embedding=json.dumps(embedding)
            )
            
            db.add(knowledge)
            await db.flush()
            
            # Adicionar ao vector store
            vector_store_service.add_vector(
                vector=embedding,
                metadata={
                    "knowledge_id": knowledge.id,
                    "organization_id": organization_id,
                    "title": title,
                    "category": category
                }
            )
            
            # Salvar índice
            vector_store_service.save_index()
            
            await db.commit()
            
            logger.info(f"Conhecimento adicionado: ID {knowledge.id}")
            
            # Retornar objeto completo
            return {
                "id": knowledge.id,
                "title": knowledge.title,
                "content": knowledge.content,
                "source": knowledge.source,
                "category": knowledge.category,
                "tags": knowledge.tags,
                "created_at": knowledge.created_at.isoformat() if knowledge.created_at else None
            }
        
        except Exception as e:
            logger.error(f"Erro ao adicionar conhecimento: {e}")
            await db.rollback()
            raise
    
    async def search_knowledge(
        self,
        db: AsyncSession,
        organization_id: int,
        query: str,
        k: Optional[int] = None,
        category_filter: Optional[str] = None,
        tags_filter: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Buscar conhecimento relevante
        """
        try:
            k = k or self.top_k
            
            # Gerar embedding da query
            query_embedding = embedding_service.generate_embedding(query)
            
            # Buscar no vector store
            results = vector_store_service.search(query_embedding, k=k * 2)
            
            # Filtrar por organização e buscar detalhes no banco
            knowledge_results = []
            
            for idx, distance, metadata in results:
                if metadata.get("organization_id") != organization_id:
                    continue
                
                knowledge_id = metadata.get("knowledge_id")
                if not knowledge_id:
                    continue
                
                # Buscar no banco
                query_builder = select(KnowledgeBase).where(
                    KnowledgeBase.id == knowledge_id,
                    KnowledgeBase.is_active == True
                )
                
                # Aplicar filtro de categoria se fornecido
                if category_filter:
                    query_builder = query_builder.where(KnowledgeBase.category == category_filter)
                
                result = await db.execute(query_builder)
                knowledge = result.scalar_one_or_none()
                
                # Aplicar filtro de tags se fornecido
                if knowledge and tags_filter:
                    knowledge_tags = json.loads(knowledge.tags) if knowledge.tags else []
                    # Verificar se alguma tag do filtro está nas tags do conhecimento
                    if not any(tag in knowledge_tags for tag in tags_filter):
                        continue
                
                if knowledge:
                    knowledge_results.append({
                        "id": knowledge.id,
                        "title": knowledge.title,
                        "content": knowledge.content,
                        "source": knowledge.source,
                        "category": knowledge.category,
                        "distance": distance,
                        "similarity": 1 / (1 + distance)  # Converter distância em similaridade
                    })
                
                if len(knowledge_results) >= k:
                    break
            
            logger.info(f"Busca realizada: {len(knowledge_results)} resultados")
            
            return knowledge_results
        
        except Exception as e:
            logger.error(f"Erro ao buscar conhecimento: {e}")
            raise
    
    async def generate_with_context(
        self,
        db: AsyncSession,
        organization_id: int,
        query: str,
        system_prompt: str,
        model: str = "gpt-4.1-mini"
    ) -> Dict[str, Any]:
        """
        Gerar resposta usando RAG
        """
        try:
            # Buscar contexto relevante
            context_results = await self.search_knowledge(
                db=db,
                organization_id=organization_id,
                query=query
            )
            
            # Montar contexto
            context_text = "\n\n".join([
                f"[{r['title']}]\n{r['content']}"
                for r in context_results
            ])
            
            # Criar prompt enriquecido
            enriched_prompt = f"""Contexto relevante da base de conhecimento:

{context_text}

---

Pergunta do usuário: {query}

Responda baseando-se no contexto fornecido acima. Se o contexto não contiver informações suficientes, indique isso na resposta."""
            
            # Gerar resposta
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": enriched_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            
            logger.info(f"Resposta RAG gerada com {len(context_results)} contextos")
            
            return {
                "answer": answer,
                "context_used": context_results,
                "model": model
            }
        
        except Exception as e:
            logger.error(f"Erro ao gerar resposta RAG: {e}")
            raise
    
    async def delete_knowledge(
        self,
        db: AsyncSession,
        knowledge_id: int,
        organization_id: int
    ) -> bool:
        """
        Deletar conhecimento
        """
        try:
            result = await db.execute(
                select(KnowledgeBase).where(
                    KnowledgeBase.id == knowledge_id,
                    KnowledgeBase.organization_id == organization_id
                )
            )
            knowledge = result.scalar_one_or_none()
            
            if not knowledge:
                return False
            
            # Marcar como inativo
            knowledge.is_active = False
            await db.commit()
            
            logger.info(f"Conhecimento deletado: ID {knowledge_id}")
            
            return True
        
        except Exception as e:
            logger.error(f"Erro ao deletar conhecimento: {e}")
            raise
    
    async def list_knowledge(
        self,
        db: AsyncSession,
        organization_id: int,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Listar conhecimentos da organização
        """
        try:
            query = select(KnowledgeBase).where(
                KnowledgeBase.organization_id == organization_id,
                KnowledgeBase.is_active == True
            )
            
            if category:
                query = query.where(KnowledgeBase.category == category)
            
            query = query.limit(limit).offset(offset)
            
            result = await db.execute(query)
            knowledges = result.scalars().all()
            
            return [
                {
                    "id": k.id,
                    "title": k.title,
                    "content": k.content[:200] + "..." if len(k.content) > 200 else k.content,
                    "source": k.source,
                    "category": k.category,
                    "created_at": k.created_at.isoformat() if k.created_at else None
                }
                for k in knowledges
            ]
        
        except Exception as e:
            logger.error(f"Erro ao listar conhecimentos: {e}")
            raise


# Instância global do serviço
rag_service = RAGService()
