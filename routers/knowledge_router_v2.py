"""
Rotas de Knowledge Base com pgvector
Implementado conforme especificação dos programadores - 15/11/2025
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from typing import Optional, List
from pydantic import BaseModel
import logging
import asyncio

from database.database import get_db
from database.models import User, Organization
from database.knowledge_model import Knowledge
from auth.security import get_current_active_user
from services.embedding_service import embedding_service
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/knowledge", tags=["Knowledge Base"])


# ========== SCHEMAS ==========

class KnowledgeCreate(BaseModel):
    """Schema para criar documento"""
    title: str
    content: str
    category: Optional[str] = None
    source: Optional[str] = None


class KnowledgeOut(BaseModel):
    """Schema de resposta de documento"""
    id: int
    title: str
    content: str
    category: Optional[str] = None
    source: Optional[str] = None
    organization_id: int
    created_at: str
    
    class Config:
        from_attributes = True


class SearchResult(BaseModel):
    """Resultado de busca com score de similaridade"""
    id: int
    title: str
    content: str
    category: Optional[str] = None
    score: float


class RAGRequest(BaseModel):
    """Request para pergunta RAG"""
    question: str


class RAGResponse(BaseModel):
    """Resposta RAG"""
    answer: str
    sources: List[SearchResult]


# ========== HELPER FUNCTIONS ==========

async def get_current_org(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Organization:
    """
    Obter organização do usuário atual
    """
    result = await db.execute(
        select(Organization).where(Organization.id == current_user.organization_id)
    )
    org = result.scalar_one_or_none()
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organização não encontrada"
        )
    
    return org


# ========== ENDPOINTS ==========

@router.post("/", response_model=KnowledgeOut, status_code=status.HTTP_201_CREATED)
async def add_knowledge(
    item: KnowledgeCreate,
    db: AsyncSession = Depends(get_db),
    current_org: Organization = Depends(get_current_org)
):
    """
    Adicionar documento à base de conhecimento
    Gera embedding automaticamente
    """
    try:
        logger.info(f"📝 Adicionando documento: {item.title}")
        
        # Gerar embedding de forma assíncrona
        embedding = await asyncio.to_thread(
            embedding_service.generate_embedding,
            item.content
        )
        
        if not embedding:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Falha ao gerar embedding"
            )
        
        # Criar documento
        new_doc = Knowledge(
            title=item.title,
            category=item.category,
            content=item.content,
            source=item.source,
            embedding=embedding,
            organization_id=current_org.id
        )
        
        db.add(new_doc)
        await db.commit()
        await db.refresh(new_doc)
        
        logger.info(f"✅ Documento adicionado: ID {new_doc.id}")
        
        return KnowledgeOut(
            id=new_doc.id,
            title=new_doc.title,
            content=new_doc.content,
            category=new_doc.category,
            source=new_doc.source,
            organization_id=new_doc.organization_id,
            created_at=new_doc.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao adicionar documento: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao adicionar documento: {str(e)}"
        )


@router.get("/", response_model=List[KnowledgeOut])
async def list_knowledge(
    category: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_org: Organization = Depends(get_current_org)
):
    """
    Listar documentos da organização
    """
    try:
        query = select(Knowledge).where(
            Knowledge.organization_id == current_org.id,
            Knowledge.is_active == True
        )
        
        if category:
            query = query.where(Knowledge.category == category)
        
        query = query.limit(limit).offset(offset).order_by(Knowledge.created_at.desc())
        
        result = await db.execute(query)
        docs = result.scalars().all()
        
        return [
            KnowledgeOut(
                id=doc.id,
                title=doc.title,
                content=doc.content,
                category=doc.category,
                source=doc.source,
                organization_id=doc.organization_id,
                created_at=doc.created_at.isoformat()
            )
            for doc in docs
        ]
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar documentos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar documentos: {str(e)}"
        )


@router.get("/search", response_model=List[SearchResult])
async def search_knowledge(
    query: str,
    limit: int = 5,
    db: AsyncSession = Depends(get_db),
    current_org: Organization = Depends(get_current_org)
):
    """
    Buscar documentos por similaridade semântica
    Usa operador <=> do pgvector (distância L2)
    """
    try:
        logger.info(f"🔍 Buscando: {query}")
        
        # Gerar embedding da query
        query_emb = await asyncio.to_thread(
            embedding_service.generate_embedding,
            query
        )
        
        if not query_emb:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Falha ao gerar embedding da query"
            )
        
        # Buscar por similaridade usando pgvector
        # <=> é o operador de distância L2
        # 1 - distance converte para score de similaridade (0-1)
        stmt = text("""
            SELECT 
                id, 
                title, 
                content, 
                category,
                1 - (embedding <=> :query_emb::vector) AS score
            FROM knowledge
            WHERE organization_id = :org_id
              AND is_active = true
            ORDER BY embedding <=> :query_emb::vector
            LIMIT :limit
        """)
        
        result = await db.execute(
            stmt,
            {
                "query_emb": str(query_emb),
                "org_id": current_org.id,
                "limit": limit
            }
        )
        
        rows = result.fetchall()
        
        results = [
            SearchResult(
                id=row[0],
                title=row[1],
                content=row[2],
                category=row[3],
                score=float(row[4])
            )
            for row in rows
        ]
        
        logger.info(f"✅ Encontrados {len(results)} documentos")
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao buscar documentos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar documentos: {str(e)}"
        )


@router.post("/rag", response_model=RAGResponse)
async def ask_rag(
    request: RAGRequest,
    db: AsyncSession = Depends(get_db),
    current_org: Organization = Depends(get_current_org)
):
    """
    Perguntar usando RAG (Retrieval-Augmented Generation)
    1. Busca documentos relevantes
    2. Monta contexto
    3. Gera resposta com GPT-4
    """
    try:
        logger.info(f"❓ Pergunta RAG: {request.question}")
        
        # 1. Buscar documentos relevantes
        docs = await search_knowledge(
            query=request.question,
            limit=5,
            db=db,
            current_org=current_org
        )
        
        if not docs:
            return RAGResponse(
                answer="Desculpe, não encontrei informações relevantes na base de conhecimento para responder sua pergunta.",
                sources=[]
            )
        
        # 2. Montar contexto
        context = "\n\n".join([
            f"[Documento {i+1}: {doc.title}]\n{doc.content}"
            for i, doc in enumerate(docs)
        ])
        
        # 3. Gerar resposta com GPT-4
        prompt = f"""Contexto (base de conhecimento):
{context}

Pergunta: {request.question}

Responda a pergunta usando APENAS as informações do contexto acima. 
Se a resposta não estiver no contexto, diga que não tem essa informação.
Seja claro, objetivo e educativo."""
        
        # Fazer requisição para OpenAI
        import requests
        
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "Você é um assistente educacional que responde perguntas baseado em documentos fornecidos."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500,
            "temperature": 0.2
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        
        answer = response.json()["choices"][0]["message"]["content"].strip()
        
        logger.info(f"✅ Resposta RAG gerada")
        
        return RAGResponse(
            answer=answer,
            sources=docs
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro no RAG: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar pergunta: {str(e)}"
        )


@router.get("/count")
async def get_count(
    db: AsyncSession = Depends(get_db),
    current_org: Organization = Depends(get_current_org)
):
    """
    Obter contagem de documentos da organização
    """
    try:
        result = await db.execute(
            select(func.count(Knowledge.id)).where(
                Knowledge.organization_id == current_org.id,
                Knowledge.is_active == True
            )
        )
        count = result.scalar()
        
        return {"count": count}
        
    except Exception as e:
        logger.error(f"❌ Erro ao contar documentos: {e}")
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
    Deletar documento (soft delete)
    """
    try:
        result = await db.execute(
            select(Knowledge).where(
                Knowledge.id == knowledge_id,
                Knowledge.organization_id == current_org.id
            )
        )
        doc = result.scalar_one_or_none()
        
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento não encontrado"
            )
        
        doc.is_active = False
        await db.commit()
        
        logger.info(f"✅ Documento deletado: ID {knowledge_id}")
        
        return {"success": True, "message": "Documento deletado com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao deletar documento: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar documento: {str(e)}"
        )
