"""
Configuração do banco de dados PostgreSQL
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import settings

# Engine assíncrono
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db():
    """
    Dependency para obter sessão do banco de dados
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Inicializar banco de dados (criar tabelas)
    Retry logic para aguardar o banco estar pronto
    """
    import asyncio
    import logging
    from database.models import Base
    
    logger = logging.getLogger(__name__)
    max_retries = 10
    retry_delay = 3  # segundos
    
    for attempt in range(1, max_retries + 1):
        try:
            async with engine.begin() as conn:
                # Criar todas as tabelas
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database initialized successfully")
            return
        except Exception as e:
            if attempt < max_retries:
                logger.warning(f"Database init attempt {attempt}/{max_retries} failed: {e}. Retrying in {retry_delay}s...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"Database init failed after {max_retries} attempts: {e}")
                raise
