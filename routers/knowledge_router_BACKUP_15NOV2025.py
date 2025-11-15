"""
Rotas de Knowledge Base (FT9-Memory) - VERSÃO CORRIGIDA
Correções implementadas em 15/11/2025:
- Endpoints públicos (sem autenticação JWT)
- Endpoint /search com GET
- organization_id como parâmetro obrigatório
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from database import get_db
from services import rag_service
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/knowledge", tags=["Knowledge Base"])


class AddKnowledgeRequest(BaseModel):
    organization_id: int
    title: str
    content: str
    source: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class RAGQueryRequest(BaseModel):
    organization_id: int
    query: str
    system_prompt: Optional[str] = None


@router.post("/")
async def add_knowledge(
    request: AddKnowledgeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Adicionar conhecimento à base (endpoint público)
    """
    try:
        knowledge = await rag_service.add_knowledge(
            db=db,
            organization_id=request.organization_id,
            title=request.title,
            content=request.content,
            source=request.source,
            category=request.category,
            tags=request.tags
        )
        
        return knowledge
    
    except Exception as e:
        logger.error(f"Erro ao adicionar conhecimento: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/")
async def list_knowledge(
    organization_id: int = Query(..., description="ID da organização"),
    category: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    Listar conhecimentos da organização (endpoint público)
    """
    try:
        knowledges = await rag_service.list_knowledge(
            db=db,
            organization_id=organization_id,
            category=category,
            limit=limit,
            offset=offset
        )
        
        return knowledges
    
    except Exception as e:
        logger.error(f"Erro ao listar conhecimentos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/search")
async def search_knowledge(
    organization_id: int = Query(..., description="ID da organização"),
    query: str = Query(..., description="Texto da busca"),
    k: int = Query(3, description="Número de resultados"),
    db: AsyncSession = Depends(get_db)
):
    """
    Buscar conhecimento relevante (endpoint público com GET)
    """
    try:
        results = await rag_service.search_knowledge(
            db=db,
            organization_id=organization_id,
            query=query,
            k=k
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
    db: AsyncSession = Depends(get_db)
):
    """
    Fazer pergunta usando RAG (endpoint público)
    """
    try:
        from config import settings
        
        system_prompt = request.system_prompt or settings.ft9_system_prompt
        
        result = await rag_service.generate_with_context(
            db=db,
            organization_id=request.organization_id,
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
    organization_id: int = Query(..., description="ID da organização"),
    db: AsyncSession = Depends(get_db)
):
    """
    Deletar conhecimento (endpoint público)
    """
    try:
        success = await rag_service.delete_knowledge(
            db=db,
            knowledge_id=knowledge_id,
            organization_id=organization_id
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
    organization_id: int = Query(..., description="ID da organização"),
    db: AsyncSession = Depends(get_db)
):
    """
    Obter estatísticas da base de conhecimento (endpoint público)
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
                KnowledgeBase.organization_id == organization_id,
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


@router.get("/count")
async def get_count(
    organization_id: int = Query(..., description="ID da organização"),
    db: AsyncSession = Depends(get_db)
):
    """
    Obter contagem de documentos da organização (endpoint público)
    Usado pelo Dashboard para exibir estatísticas
    """
    try:
        from sqlalchemy import select, func
        from database import KnowledgeBase
        
        result = await db.execute(
            select(func.count(KnowledgeBase.id)).where(
                KnowledgeBase.organization_id == organization_id,
                KnowledgeBase.is_active == True
            )
        )
        count = result.scalar()
        
        return {"count": count if count else 0}
        
    except Exception as e:
        logger.error(f"Erro ao contar documentos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
