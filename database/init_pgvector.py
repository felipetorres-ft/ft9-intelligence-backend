"""
Script para inicializar extensão pgvector no PostgreSQL
Implementado conforme especificação dos programadores - 15/11/2025
"""
import asyncio
import logging
from sqlalchemy import text
from database.database import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_pgvector():
    """
    Habilitar extensão pgvector no PostgreSQL
    Necessário para suporte a vetores e busca semântica
    """
    try:
        async with engine.begin() as conn:
            # Verificar se a extensão já existe
            result = await conn.execute(
                text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
            )
            exists = result.scalar()
            
            if not exists:
                # Criar extensão pgvector
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                logger.info("✅ Extensão pgvector criada com sucesso")
            else:
                logger.info("✅ Extensão pgvector já existe")
            
            # Verificar versão
            result = await conn.execute(
                text("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
            )
            version = result.scalar()
            logger.info(f"📦 pgvector versão: {version}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar pgvector: {e}")
        logger.warning("⚠️  Se o erro for 'extension \"vector\" is not available', você precisa instalar pgvector no PostgreSQL")
        logger.warning("⚠️  Railway: pgvector já vem instalado por padrão")
        logger.warning("⚠️  Local: instale com 'apt-get install postgresql-15-pgvector' ou via Docker")
        return False


async def test_vector_operations():
    """
    Testar operações básicas com vetores
    """
    try:
        async with engine.begin() as conn:
            # Criar tabela de teste
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS test_vectors (
                    id SERIAL PRIMARY KEY,
                    embedding vector(3)
                )
            """))
            
            # Inserir vetor de teste
            await conn.execute(text("""
                INSERT INTO test_vectors (embedding) 
                VALUES ('[1,2,3]')
            """))
            
            # Buscar por similaridade (distância L2)
            result = await conn.execute(text("""
                SELECT id, embedding <-> '[1,2,3]' AS distance
                FROM test_vectors
                ORDER BY distance
                LIMIT 1
            """))
            row = result.fetchone()
            
            logger.info(f"✅ Teste de operações vetoriais: OK (distance={row[1]})")
            
            # Limpar tabela de teste
            await conn.execute(text("DROP TABLE IF EXISTS test_vectors"))
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro ao testar operações vetoriais: {e}")
        return False


async def main():
    """
    Executar inicialização e testes
    """
    logger.info("🚀 Iniciando configuração pgvector...")
    
    # Inicializar extensão
    success = await init_pgvector()
    if not success:
        logger.error("❌ Falha ao inicializar pgvector")
        return False
    
    # Testar operações
    success = await test_vector_operations()
    if not success:
        logger.error("❌ Falha nos testes de operações vetoriais")
        return False
    
    logger.info("✅ pgvector configurado e testado com sucesso!")
    return True


if __name__ == "__main__":
    asyncio.run(main())
