# knowledge_router.py — FT9 Intelligence
# Versão AI9 — Rotas completas: ADD, SEARCH, RAG, COUNT

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import sqlalchemy as sa
import openai

from database import get_async_session
from models.knowledge import Knowledge
from services.embedding_service import generate_embedding
from schemas.knowledge_schemas import KnowledgeCreate, KnowledgeOut

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])

# -----------------------------------------------------
# 1) ADD — adicionar documento na Knowledge Base
# -----------------------------------------------------
@router.post("/", response_model=KnowledgeOut)
async def add_knowledge(
    payload: KnowledgeCreate,
    session: AsyncSession = Depends(get_async_session)
):
    # Gerar embedding
    embedding = await generate_embedding(payload.content)
    
    new_doc = Knowledge(
        title=payload.title,
        category=payload.category,
        content=payload.content,
        embedding=embedding,
        organization_id=1  # Ajustar se houver multi-tenant real
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
# 3) SEARCH — busca por similaridade (pgvector)
# -----------------------------------------------------
@router.get("/search", response_model=list[KnowledgeOut])
async def search_knowledge(
    query: str,
    session: AsyncSession = Depends(get_async_session)
):
    query_emb = await generate_embedding(query)
    
    stmt = sa.text("""
        SELECT id, title, category, content, created_at,
               1 - (embedding <=> :query_emb) AS score
        FROM knowledge
        ORDER BY embedding <=> :query_emb
        LIMIT 5;
    """)
    
    result = await session.execute(stmt, {"query_emb": query_emb})
    rows = result.fetchall()
    
    return [
        KnowledgeOut(
            id=r.id,
            title=r.title,
            category=r.category,
            content=r.content,
            created_at=r.created_at
        )
        for r in rows
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
