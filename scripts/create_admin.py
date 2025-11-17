"""
Script para criar usuário admin no banco de dados
"""
import asyncio
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.database import AsyncSessionLocal
from database.models import User, Organization
from auth import get_password_hash


async def create_admin():
    """Criar usuário admin"""
    async with AsyncSessionLocal() as session:
        try:
            # Verificar se usuário já existe
            from sqlalchemy import select
            result = await session.execute(
                select(User).where(User.email == "ft9.admin@ft9.com.br")
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"❌ Usuário {existing_user.email} já existe!")
                print(f"   ID: {existing_user.id}")
                print(f"   Atualizando senha...")
                
                # Atualizar senha
                existing_user.hashed_password = get_password_hash("FT9@2025!")
                existing_user.is_active = True
                existing_user.is_superuser = True
                await session.commit()
                print("✅ Senha atualizada com sucesso!")
                return
            
            # Criar novo usuário
            user = User(
                email="ft9.admin@ft9.com.br",
                username="ft9admin",
                hashed_password=get_password_hash("FT9@2025!"),
                full_name="Admin FT9",
                is_active=True,
                is_superuser=True,
                org_id=19
            )
            
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            print("✅ Usuário admin criado com sucesso!")
            print(f"   Email: {user.email}")
            print(f"   ID: {user.id}")
            print(f"   Org ID: {user.org_id}")
            print(f"   Superuser: {user.is_superuser}")
            
        except Exception as e:
            print(f"❌ Erro ao criar usuário: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    print("🔧 Criando usuário admin...")
    asyncio.run(create_admin())
