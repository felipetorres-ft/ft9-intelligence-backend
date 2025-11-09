"""
Script de inicialização do banco de dados para produção
Cria tabelas e organização demo se não existirem
"""
import asyncio
from database import init_db, get_db
from database.models import Organization, User
from auth.security import get_password_hash
from sqlalchemy import select
import os

async def init_production_db():
    """Inicializa banco de dados em produção"""
    print("🚀 Inicializando banco de dados...")
    
    # Criar tabelas
    await init_db()
    print("✅ Tabelas criadas/verificadas")
    
    # Verificar se já existe organização demo
    async for db in get_db():
        result = await db.execute(
            select(Organization).where(Organization.slug == "clinica-demo-ft9")
        )
        existing_org = result.scalar_one_or_none()
        
        if existing_org:
            print("ℹ️  Organização demo já existe")
            return
        
        # Criar organização demo
        org = Organization(
            name="Clínica Demo FT9",
            slug="clinica-demo-ft9",
            subscription_plan="professional",
            subscription_status="trial",
            is_active=True
        )
        db.add(org)
        await db.flush()
        
        # Criar usuário admin
        user = User(
            email="admin@ft9.com.br",
            hashed_password=get_password_hash("ft9demo"),
            full_name="Admin FT9",
            role="ORG_ADMIN",
            organization_id=org.id,
            is_active=True
        )
        db.add(user)
        await db.commit()
        
        print("✅ Organização demo criada:")
        print(f"   📧 Email: admin@ft9.com.br")
        print(f"   🔑 Senha: ft9demo")
        print(f"   🏢 Org: {org.name}")
        
        break

if __name__ == "__main__":
    asyncio.run(init_production_db())
