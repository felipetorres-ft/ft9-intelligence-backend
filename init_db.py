"""
Script para inicializar o banco de dados PostgreSQL
"""
import asyncio
import sys
from database import init_db, AsyncSessionLocal, Organization, User
from auth import get_password_hash
from database.models import UserRole, SubscriptionPlan, SubscriptionStatus
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_demo_organization():
    """
    Criar organização de demonstração
    """
    async with AsyncSessionLocal() as session:
        try:
            # Criar organização demo
            demo_org = Organization(
                name="Clínica Demo FT9",
                slug="clinica-demo-ft9",
                email="demo@ft9.com.br",
                phone="+55 11 99999-9999",
                address="Rua Demo, 123",
                city="São Paulo",
                state="SP",
                country="BR",
                subscription_plan=SubscriptionPlan.PROFESSIONAL,
                subscription_status=SubscriptionStatus.TRIAL,
                subscription_started_at=datetime.utcnow(),
                subscription_expires_at=datetime.utcnow() + timedelta(days=14),
                is_active=True
            )
            
            session.add(demo_org)
            await session.flush()
            
            # Criar usuário admin demo
            demo_admin = User(
                organization_id=demo_org.id,
                email="admin@ft9.com.br",
                hashed_password=get_password_hash("ft9demo"),
                full_name="Administrador Demo",
                phone="+55 11 99999-9999",
                role=UserRole.ORG_ADMIN,
                is_active=True,
                is_verified=True
            )
            
            session.add(demo_admin)
            await session.commit()
            
            logger.info("=" * 60)
            logger.info("✅ Organização de demonstração criada com sucesso!")
            logger.info("=" * 60)
            logger.info(f"Organização: {demo_org.name}")
            logger.info(f"Slug: {demo_org.slug}")
            logger.info(f"Plano: {demo_org.subscription_plan.value}")
            logger.info("-" * 60)
            logger.info("Credenciais de acesso:")
            logger.info(f"Email: {demo_admin.email}")
            logger.info(f"Senha: ft9demo")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Erro ao criar organização demo: {e}")
            await session.rollback()
            raise


async def main():
    """
    Função principal
    """
    try:
        logger.info("Inicializando banco de dados...")
        
        # Criar tabelas
        await init_db()
        logger.info("✅ Tabelas criadas com sucesso!")
        
        # Criar organização demo
        await create_demo_organization()
        
        logger.info("\n🎉 Banco de dados inicializado com sucesso!")
        logger.info("\nPróximos passos:")
        logger.info("1. Faça login com as credenciais acima")
        logger.info("2. Configure o número do WhatsApp Business")
        logger.info("3. Comece a receber mensagens!")
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar banco de dados: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
