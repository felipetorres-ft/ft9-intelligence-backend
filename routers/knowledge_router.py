# knowledge_router.py — FT9 Intelligence
# Versão AI9 — Rotas completas: ADD, SEARCH, RAG, COUNT

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import sqlalchemy as sa
import openai

from database import get_async_session, User
from models.knowledge import Knowledge
from services.embedding_service import generate_embedding
from schemas.knowledge_schemas import KnowledgeCreate, KnowledgeOut
from auth import get_current_active_user

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])

# -----------------------------------------------------
# 1) ADD — adicionar documento na Knowledge Base
# -----------------------------------------------------
@router.post("/", response_model=KnowledgeOut)
async def add_knowledge(
    payload: KnowledgeCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    # Gerar embedding
    embedding = await generate_embedding(payload.content)
    
    # Converter embedding para JSON string
    import json
    embedding_json = json.dumps(embedding) if embedding else None
    
    new_doc = Knowledge(
        title=payload.title,
        category=payload.category,
        content=payload.content,
        embedding=embedding_json,
        organization_id=current_user.organization_id
    )
    
    session.add(new_doc)
    await session.commit()
    await session.refresh(new_doc)
    
    return new_doc

# -----------------------------------------------------
# 2) COUNT — contar documentos
# -----------------------------------------------------
@router.get("/count")
async def count_knowledge(
    session: AsyncSession = Depends(get_async_session)
):
    q = await session.execute(select(sa.func.count(Knowledge.id)))
    return {"count": q.scalar()}

# -----------------------------------------------------
# 3) SEARCH — busca por similaridade (fallback sem pgvector)
# -----------------------------------------------------
@router.get("/search", response_model=list[KnowledgeOut])
async def search_knowledge(
    query: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    import json
    import numpy as np
    
    query_emb = await generate_embedding(query)
    
    # Buscar todos os documentos da organização
    stmt = select(Knowledge).where(Knowledge.organization_id == current_user.organization_id)
    result = await session.execute(stmt)
    docs = result.scalars().all()
    
    if not docs:
        return []
    
    # Calcular similaridade de cosseno em Python
    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    scored_docs = []
    for doc in docs:
        if doc.embedding:
            # Converter JSON string para lista
            doc_emb = json.loads(doc.embedding) if isinstance(doc.embedding, str) else doc.embedding
            score = cosine_similarity(query_emb, doc_emb)
            scored_docs.append((doc, score))
    
    # Ordenar por score (maior primeiro) e pegar top 5
    scored_docs.sort(key=lambda x: x[1], reverse=True)
    top_docs = [doc for doc, score in scored_docs[:5]]
    
    return [
        KnowledgeOut(
            id=doc.id,
            title=doc.title,
            category=doc.category,
            content=doc.content,
            created_at=doc.created_at
        )
        for doc in top_docs
    ]

# -----------------------------------------------------
# 4) RAG — resposta baseada em contexto (FT9 + OpenAI)
# -----------------------------------------------------
@router.post("/rag")
async def ask_rag(
    question: str,
    session: AsyncSession = Depends(get_async_session)
):
    # 1) Buscar contexto
    context_docs = await search_knowledge(question, session)
    
    if not context_docs:
        raise HTTPException(404, "Nenhum documento encontrado para RAG.")
    
    # 2) Montar contexto
    context_text = "\n---\n".join([doc.content for doc in context_docs])
    
    prompt = f"""
Responda a seguinte pergunta usando SOMENTE o contexto abaixo
e seguindo a metodologia FT9 (9 Pilares + PTC).

Pergunta:
{question}

Contexto:
{context_text}

Resposta:
"""
    
    # 3) Chamar OpenAI
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=400
    )
    
    return {"answer": resp.choices[0].message["content"]}
