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


async def ensure_database_exists():
    """
    Garantir que o banco de dados existe, criando se necessário
    """
    import asyncpg
    import logging
    from urllib.parse import urlparse
    
    logger = logging.getLogger(__name__)
    
    # Parse DATABASE_URL
    parsed = urlparse(settings.DATABASE_URL)
    db_name = parsed.path.lstrip('/')
    
    # Construir URL para template1 mantendo as credenciais corretas
    template_url = f"postgresql://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port or 5432}/template1"
    
    try:
        # Conectar no template1
        conn = await asyncpg.connect(template_url)
        
        # Verificar se o banco existe
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            db_name
        )
        
        if not exists:
            # Criar o banco
            await conn.execute(f'CREATE DATABASE "{db_name}"')
            logger.info(f"Database '{db_name}' created successfully")
        else:
            logger.info(f"Database '{db_name}' already exists")
        
        await conn.close()
        return True
    except Exception as e:
        logger.error(f"Error ensuring database exists: {e}")
        return False


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
    
    # Primeiro, garantir que o banco existe
    await ensure_database_exists()
    
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
