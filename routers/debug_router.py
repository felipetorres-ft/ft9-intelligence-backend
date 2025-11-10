"""
Router de debug para testar banco de dados
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database import get_db
import traceback

router = APIRouter(prefix="/api/debug", tags=["Debug"])


@router.get("/db-test")
async def test_database(db: AsyncSession = Depends(get_db)):
    """Testar conexão e estrutura do banco"""
    try:
        result = {}
        
        # Testar conexão
        await db.execute(text("SELECT 1"))
        result["connection"] = "✅ OK"
        
        # Listar tabelas
        tables_query = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables_result = await db.execute(tables_query)
        tables = [row[0] for row in tables_result.fetchall()]
        result["tables"] = tables
        
        # Contar organizações
        try:
            count_result = await db.execute(text("SELECT COUNT(*) FROM organizations"))
            org_count = count_result.scalar()
            result["organizations_count"] = org_count
        except Exception as e:
            result["organizations_count"] = f"❌ Erro: {str(e)}"
        
        # Contar usuários
        try:
            count_result = await db.execute(text("SELECT COUNT(*) FROM users"))
            user_count = count_result.scalar()
            result["users_count"] = user_count
        except Exception as e:
            result["users_count"] = f"❌ Erro: {str(e)}"
        
        return result
        
    except Exception as e:
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
