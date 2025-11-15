"""
Rotas de Knowledge Base (FT9-Memory) - VERSÃO HÍBRIDA
Suporta autenticação JWT (frontend) E chamadas públicas (testes)
Criado em 15/11/2025
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from database import get_db
from database.models import Organization
from routers.auth_router import get_current_org
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


class RAGQueryRequest(BaseModel):
    query: str
    system_prompt: Optional[str] = None


@router.post("/")
async def add_knowledge(
    request: AddKnowledgeRequest,
    db: AsyncSession = Depends(get_db),
    current_org: Organization = Depends(get_current_org)
):
    """
    Adicionar conhecimento à base (autenticado via JWT)
    """
    try:
        knowledge = await rag_service.add_knowledge(
            db=db,
            organization_id=current_org.id,
            title=request.title,
            content=request.content,
            source=request.source,
            category=request.category,
            tags=request.tags
        )
        
        logger.info(f"Knowledge added: {knowledge.id} for org {current_org.id}")
        
        return {
            "id": knowledge.id,
            "title": knowledge.title,
            "content": knowledge.content,
            "category": knowledge.category,
            "tags": knowledge.tags,
            "created_at": knowledge.created_at.isoformat() if knowledge.created_at else None
        }
    except Exception as e:
        logger.error(f"Error adding knowledge: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao adicionar conhecimento: {str(e)}"
        )


@router.get("/")
async def list_knowledge(
    db: AsyncSession = Depends(get_db),
    current_org: Organization = Depends(get_current_org),
    limit: int = Query(default=10, ge=1, le=100)
):
    """
    Listar conhecimentos da organização (autenticado via JWT)
    """
    try:
        knowledge_list = await rag_service.list_knowledge(
            db=db,
            organization_id=current_org.id,
            limit=limit
        )
        
        return [
            {
                "id": k.id,
                "title": k.title,
                "content": k.content[:200] + "..." if len(k.content) > 200 else k.content,
                "category": k.category,
                "tags": k.tags,
                "created_at": k.created_at.isoformat() if k.created_at else None
            }
            for k in knowledge_list
        ]
    except Exception as e:
        logger.error(f"Error listing knowledge: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar conhecimentos: {str(e)}"
        )


@router.get("/search")
async def search_knowledge(
    query: str = Query(..., description="Termo de busca"),
    db: AsyncSession = Depends(get_db),
    current_org: Organization = Depends(get_current_org),
    k: int = Query(default=5, ge=1, le=20, description="Número de resultados")
):
    """
    Buscar conhecimentos por similaridade semântica (autenticado via JWT)
    """
    try:
        results = await rag_service.search_knowledge(
            db=db,
            organization_id=current_org.id,
            query=query,
            k=k
        )
        
        return [
            {
                "id": r.id,
                "title": r.title,
                "content": r.content[:300] + "..." if len(r.content) > 300 else r.content,
                "category": r.category,
                "similarity": getattr(r, 'similarity', None),
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in results
        ]
    except Exception as e:
        logger.error(f"Error searching knowledge: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar conhecimentos: {str(e)}"
        )


@router.post("/rag")
async def rag_query(
    request: RAGQueryRequest,
    db: AsyncSession = Depends(get_db),
    current_org: Organization = Depends(get_current_org)
):
    """
    Fazer pergunta usando RAG (autenticado via JWT)
    """
    try:
        answer = await rag_service.query_with_rag(
            db=db,
            organization_id=current_org.id,
            query=request.query,
            system_prompt=request.system_prompt
        )
        
        return {
            "answer": answer.get("answer", ""),
            "sources": [
                {
                    "id": s.id,
                    "title": s.title,
                    "content": s.content[:200] + "..." if len(s.content) > 200 else s.content,
                    "similarity": getattr(s, 'similarity', None)
                }
                for s in answer.get("sources", [])
            ],
            "model": answer.get("model", "unknown")
        }
    except Exception as e:
        logger.error(f"Error in RAG query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar resposta: {str(e)}"
        )


@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_org: Organization = Depends(get_current_org)
):
    """
    Obter estatísticas da Knowledge Base (autenticado via JWT)
    """
    try:
        stats = await rag_service.get_stats(db=db, organization_id=current_org.id)
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter estatísticas: {str(e)}"
        )


@router.get("/count")
async def get_count(
    db: AsyncSession = Depends(get_db),
    organization_id: Optional[int] = Query(None, description="ID da organização (público)"),
    current_org: Optional[Organization] = Depends(get_current_org)
):
    """
    Obter contagem de documentos
    Suporta JWT (frontend) ou organization_id (público)
    """
    try:
        # Priorizar JWT se disponível, senão usar organization_id público
        org_id = current_org.id if current_org else organization_id
        
        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="organization_id é obrigatório quando não autenticado"
            )
        
        from database.models import KnowledgeBase
        from sqlalchemy import select, func
        
        result = await db.execute(
            select(func.count(KnowledgeBase.id))
            .where(KnowledgeBase.organization_id == org_id)
        )
        count = result.scalar() or 0
        
        return {"count": count}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting count: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao contar documentos: {str(e)}"
        )


@router.delete("/{knowledge_id}")
async def delete_knowledge(
    knowledge_id: int,
    db: AsyncSession = Depends(get_db),
    current_org: Organization = Depends(get_current_org)
):
    """
    Deletar conhecimento (autenticado via JWT)
    """
    try:
        success = await rag_service.delete_knowledge(
            db=db,
            knowledge_id=knowledge_id,
            organization_id=current_org.id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conhecimento não encontrado"
            )
        
        return {"message": "Conhecimento deletado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting knowledge: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar conhecimento: {str(e)}"
        )
