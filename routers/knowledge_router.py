"""
Rotas de Knowledge Base (FT9-Memory)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from database import get_db, User
from auth import get_current_active_user
from services import rag_service
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/knowledge", tags=["Knowledge Base"])


class AddKnowledgeRequest(BaseModel):
    title: str
    content: str
    source: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class SearchKnowledgeRequest(BaseModel):
    query: str
    k: Optional[int] = 3


class RAGQueryRequest(BaseModel):
    query: str
    system_prompt: Optional[str] = None


@router.post("/")
async def add_knowledge(
    request: AddKnowledgeRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Adicionar conhecimento à base
    """
    try:
        knowledge = await rag_service.add_knowledge(
            db=db,
            organization_id=current_user.organization_id,
            title=request.title,
            content=request.content,
            source=request.source,
            category=request.category,
            tags=request.tags
        )
        
        # Retornar objeto completo (compatível com frontend)
        return knowledge
    
    except Exception as e:
        logger.error(f"Erro ao adicionar conhecimento: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/")
async def list_knowledge(
    category: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Listar conhecimentos da organização
    """
    try:
        knowledges = await rag_service.list_knowledge(
            db=db,
            organization_id=current_user.organization_id,
            category=category,
            limit=limit,
            offset=offset
        )
        
        # Retornar array diretamente (compatível com frontend)
        return knowledges
    
    except Exception as e:
        logger.error(f"Erro ao listar conhecimentos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/search")
async def search_knowledge(
    request: SearchKnowledgeRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Buscar conhecimento relevante
    """
    try:
        results = await rag_service.search_knowledge(
            db=db,
            organization_id=current_user.organization_id,
            query=request.query,
            k=request.k
        )
        
        return {
            "results": results,
            "total": len(results)
        }
    
    except Exception as e:
        logger.error(f"Erro ao buscar conhecimento: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/rag")
async def rag_query(
    request: RAGQueryRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Fazer pergunta usando RAG (Retrieval-Augmented Generation)
    """
    try:
        from config import settings
        
        system_prompt = request.system_prompt or settings.ft9_system_prompt
        
        result = await rag_service.generate_with_context(
            db=db,
            organization_id=current_user.organization_id,
            query=request.query,
            system_prompt=system_prompt
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Erro ao processar RAG query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{knowledge_id}")
async def delete_knowledge(
    knowledge_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Deletar conhecimento
    """
    try:
        success = await rag_service.delete_knowledge(
            db=db,
            knowledge_id=knowledge_id,
            organization_id=current_user.organization_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conhecimento não encontrado"
            )
        
        return {
            "success": True,
            "message": "Conhecimento deletado com sucesso"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar conhecimento: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/stats")
async def get_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obter estatísticas da base de conhecimento
    """
    try:
        from services import vector_store_service
        from sqlalchemy import select, func
        from database import KnowledgeBase
        
        # Stats do vector store
        vector_stats = vector_store_service.get_stats()
        
        # Stats do banco de dados
        result = await db.execute(
            select(func.count(KnowledgeBase.id)).where(
                KnowledgeBase.organization_id == current_user.organization_id,
                KnowledgeBase.is_active == True
            )
        )
        total_knowledge = result.scalar()
        
        return {
            "organization_knowledge_count": total_knowledge,
            "vector_store": vector_stats
        }
    
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
