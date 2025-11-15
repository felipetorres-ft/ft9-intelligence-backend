"""
Testes End-to-End para Knowledge Base com pgvector
Implementado conforme especificação dos programadores - 15/11/2025

Este script testa:
1. Conexão com banco de dados
2. Criação de documento com embedding
3. Busca semântica
4. RAG (Retrieval-Augmented Generation)
5. Contagem de documentos

Uso:
    python test_knowledge_e2e.py
"""

import asyncio
import logging
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select, func, text
from database.database import AsyncSessionLocal, init_db
from database.knowledge_model import Knowledge
from database.models import Organization
from services.embedding_service import embedding_service

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_database_connection():
    """
    Teste 1: Conexão com banco de dados
    """
    logger.info("\n" + "="*60)
    logger.info("TESTE 1: Conexão com banco de dados")
    logger.info("="*60)
    
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT version()"))
            version = result.scalar()
            logger.info(f"✅ PostgreSQL versão: {version}")
            
            # Verificar extensão pgvector
            result = await session.execute(
                text("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
            )
            pgvector_version = result.scalar()
            
            if pgvector_version:
                logger.info(f"✅ pgvector versão: {pgvector_version}")
            else:
                logger.warning("⚠️  pgvector não instalado")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro na conexão: {e}")
        return False


async def test_create_document():
    """
    Teste 2: Criar documento com embedding
    """
    logger.info("\n" + "="*60)
    logger.info("TESTE 2: Criar documento com embedding")
    logger.info("="*60)
    
    try:
        async with AsyncSessionLocal() as session:
            # Buscar primeira organização
            result = await session.execute(select(Organization).limit(1))
            org = result.scalar_one_or_none()
            
            if not org:
                logger.error("❌ Nenhuma organização encontrada")
                return False
            
            logger.info(f"🏢 Organização: {org.name} (ID: {org.id})")
            
            # Criar documento de teste
            test_content = """
            Posicionamento Estratégico é o primeiro pilar do PTC 2025.
            Ele ensina como se posicionar no mercado de forma única e diferenciada.
            O objetivo é criar uma identidade forte que atraia o cliente ideal.
            """
            
            logger.info("🔄 Gerando embedding...")
            embedding = embedding_service.generate_embedding(test_content)
            
            if not embedding:
                logger.error("❌ Falha ao gerar embedding")
                return False
            
            logger.info(f"✅ Embedding gerado ({len(embedding)} dimensões)")
            
            # Criar documento
            doc = Knowledge(
                title="[TESTE] Pilar 1 - Posicionamento Estratégico",
                category="teste",
                content=test_content,
                source="test_knowledge_e2e.py",
                embedding=embedding,
                organization_id=org.id
            )
            
            session.add(doc)
            await session.commit()
            await session.refresh(doc)
            
            logger.info(f"✅ Documento criado (ID: {doc.id})")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro ao criar documento: {e}")
        return False


async def test_semantic_search():
    """
    Teste 3: Busca semântica
    """
    logger.info("\n" + "="*60)
    logger.info("TESTE 3: Busca semântica")
    logger.info("="*60)
    
    try:
        async with AsyncSessionLocal() as session:
            # Gerar embedding da query
            query_text = "Como me posicionar no mercado?"
            logger.info(f"🔍 Query: {query_text}")
            
            logger.info("🔄 Gerando embedding da query...")
            query_emb = embedding_service.generate_embedding(query_text)
            
            if not query_emb:
                logger.error("❌ Falha ao gerar embedding da query")
                return False
            
            logger.info(f"✅ Embedding da query gerado")
            
            # Buscar documentos similares
            stmt = text("""
                SELECT 
                    id, 
                    title, 
                    content,
                    category,
                    1 - (embedding <=> :query_emb::vector) AS score
                FROM knowledge
                WHERE is_active = true
                ORDER BY embedding <=> :query_emb::vector
                LIMIT 3
            """)
            
            result = await session.execute(
                stmt,
                {"query_emb": str(query_emb)}
            )
            
            rows = result.fetchall()
            
            if not rows:
                logger.warning("⚠️  Nenhum documento encontrado")
                return False
            
            logger.info(f"\n📊 Resultados ({len(rows)}):")
            for i, row in enumerate(rows, 1):
                logger.info(f"\n{i}. {row[1]}")
                logger.info(f"   Categoria: {row[3]}")
                logger.info(f"   Score: {row[4]:.4f}")
                logger.info(f"   Preview: {row[2][:100]}...")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro na busca semântica: {e}")
        return False


async def test_document_count():
    """
    Teste 4: Contagem de documentos
    """
    logger.info("\n" + "="*60)
    logger.info("TESTE 4: Contagem de documentos")
    logger.info("="*60)
    
    try:
        async with AsyncSessionLocal() as session:
            # Contar total
            result = await session.execute(
                select(func.count(Knowledge.id)).where(Knowledge.is_active == True)
            )
            total = result.scalar()
            
            logger.info(f"✅ Total de documentos ativos: {total}")
            
            # Contar por categoria
            result = await session.execute(
                text("""
                    SELECT category, COUNT(*) 
                    FROM knowledge 
                    WHERE is_active = true 
                    GROUP BY category
                    ORDER BY COUNT(*) DESC
                """)
            )
            
            categories = result.fetchall()
            
            if categories:
                logger.info("\n📊 Documentos por categoria:")
                for cat, count in categories:
                    logger.info(f"   {cat or '(sem categoria)'}: {count}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro na contagem: {e}")
        return False


async def test_cleanup():
    """
    Teste 5: Limpeza (remover documentos de teste)
    """
    logger.info("\n" + "="*60)
    logger.info("TESTE 5: Limpeza de documentos de teste")
    logger.info("="*60)
    
    try:
        async with AsyncSessionLocal() as session:
            # Deletar documentos de teste
            result = await session.execute(
                select(Knowledge).where(Knowledge.category == "teste")
            )
            test_docs = result.scalars().all()
            
            if not test_docs:
                logger.info("✅ Nenhum documento de teste para remover")
                return True
            
            for doc in test_docs:
                doc.is_active = False
            
            await session.commit()
            
            logger.info(f"✅ {len(test_docs)} documento(s) de teste removido(s)")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro na limpeza: {e}")
        return False


async def main():
    """
    Executar todos os testes
    """
    logger.info("🚀 Iniciando testes end-to-end da Knowledge Base...")
    
    # Inicializar banco de dados
    logger.info("📦 Inicializando banco de dados...")
    await init_db()
    
    # Executar testes
    tests = [
        ("Conexão com banco de dados", test_database_connection),
        ("Criar documento com embedding", test_create_document),
        ("Busca semântica", test_semantic_search),
        ("Contagem de documentos", test_document_count),
        ("Limpeza de testes", test_cleanup)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            success = await test_func()
            results.append((name, success))
        except Exception as e:
            logger.error(f"❌ Erro no teste '{name}': {e}")
            results.append((name, False))
    
    # Resumo
    logger.info("\n" + "="*60)
    logger.info("RESUMO DOS TESTES")
    logger.info("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        logger.info(f"{status} - {name}")
    
    logger.info(f"\n📊 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        logger.info("🎉 Todos os testes passaram!")
    else:
        logger.warning(f"⚠️  {total - passed} teste(s) falharam")


if __name__ == "__main__":
    asyncio.run(main())
