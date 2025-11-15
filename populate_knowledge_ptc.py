"""
Script para popular base de conhecimento com aulas do PTC 2025
Implementado conforme especificação dos programadores - 15/11/2025

Este script:
1. Conecta ao banco de dados PostgreSQL
2. Lê as aulas do PTC da pasta knowledge_base/
3. Gera embeddings para cada aula
4. Insere na tabela knowledge

Uso:
    python populate_knowledge_ptc.py --org-id 1
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import List, Dict
import argparse

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select
from database.database import AsyncSessionLocal, init_db
from database.knowledge_model import Knowledge
from database.models import Organization
from services.embedding_service import embedding_service

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def load_ptc_lessons() -> List[Dict[str, str]]:
    """
    Carregar aulas do PTC da pasta knowledge_base/
    
    Returns:
        Lista de dicionários com title, content, category
    """
    lessons = []
    kb_path = Path(__file__).parent / "knowledge_base"
    
    if not kb_path.exists():
        logger.warning(f"Pasta {kb_path} não encontrada")
        return lessons
    
    # Procurar arquivos .txt ou .md
    for file_path in kb_path.glob("**/*.txt"):
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Extrair título do nome do arquivo
            title = file_path.stem.replace('_', ' ').title()
            
            # Determinar categoria
            category = "ptc-2025"
            if "pilar" in file_path.stem.lower():
                category = "pilar"
            elif "aula" in file_path.stem.lower():
                category = "aula"
            
            lessons.append({
                "title": title,
                "content": content,
                "category": category,
                "source": str(file_path.name)
            })
            
            logger.info(f"✅ Carregado: {title}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar {file_path}: {e}")
    
    logger.info(f"📚 Total de aulas carregadas: {len(lessons)}")
    return lessons


async def populate_knowledge(org_id: int, lessons: List[Dict[str, str]]):
    """
    Popular base de conhecimento com aulas
    
    Args:
        org_id: ID da organização
        lessons: Lista de aulas
    """
    async with AsyncSessionLocal() as session:
        try:
            # Verificar se organização existe
            result = await session.execute(
                select(Organization).where(Organization.id == org_id)
            )
            org = result.scalar_one_or_none()
            
            if not org:
                logger.error(f"❌ Organização {org_id} não encontrada")
                return
            
            logger.info(f"🏢 Organização: {org.name}")
            
            # Processar cada aula
            for i, lesson in enumerate(lessons, 1):
                logger.info(f"\n📝 [{i}/{len(lessons)}] Processando: {lesson['title']}")
                
                # Verificar se já existe
                result = await session.execute(
                    select(Knowledge).where(
                        Knowledge.title == lesson['title'],
                        Knowledge.organization_id == org_id
                    )
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    logger.warning(f"⚠️  Aula já existe, pulando...")
                    continue
                
                # Gerar embedding
                logger.info(f"🔄 Gerando embedding ({len(lesson['content'])} caracteres)...")
                embedding = embedding_service.generate_embedding(lesson['content'])
                
                if not embedding:
                    logger.error(f"❌ Falha ao gerar embedding, pulando...")
                    continue
                
                # Criar documento
                doc = Knowledge(
                    title=lesson['title'],
                    category=lesson['category'],
                    content=lesson['content'],
                    source=lesson.get('source'),
                    embedding=embedding,
                    organization_id=org_id
                )
                
                session.add(doc)
                await session.commit()
                
                logger.info(f"✅ Aula adicionada com sucesso!")
            
            logger.info(f"\n🎉 População completa! {len(lessons)} aulas processadas.")
            
        except Exception as e:
            logger.error(f"❌ Erro ao popular conhecimento: {e}")
            await session.rollback()
            raise


async def main():
    """
    Main function
    """
    parser = argparse.ArgumentParser(description='Popular base de conhecimento com aulas do PTC')
    parser.add_argument('--org-id', type=int, default=1, help='ID da organização (padrão: 1)')
    args = parser.parse_args()
    
    logger.info("🚀 Iniciando população da base de conhecimento...")
    
    # Inicializar banco de dados
    logger.info("📦 Inicializando banco de dados...")
    await init_db()
    
    # Carregar aulas
    logger.info("📚 Carregando aulas do PTC...")
    lessons = await load_ptc_lessons()
    
    if not lessons:
        logger.error("❌ Nenhuma aula encontrada!")
        logger.info("💡 Dica: Coloque os arquivos .txt das aulas na pasta knowledge_base/")
        return
    
    # Popular conhecimento
    logger.info(f"💾 Populando base de conhecimento (org_id={args.org_id})...")
    await populate_knowledge(args.org_id, lessons)
    
    logger.info("✅ Processo concluído!")


if __name__ == "__main__":
    asyncio.run(main())
