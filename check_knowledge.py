import asyncio
import os
from sqlalchemy import select, text
from database.database import AsyncSessionLocal
from database.knowledge_model import Knowledge

async def check_knowledge():
    async with AsyncSessionLocal() as session:
        # Contar total
        result = await session.execute(select(Knowledge))
        docs = result.scalars().all()
        
        print(f"Total de documentos: {len(docs)}")
        
        for doc in docs:
            print(f"\nID: {doc.id}")
            print(f"Title: {doc.title}")
            print(f"Category: {doc.category}")
            print(f"Organization ID: {doc.organization_id}")
            print(f"Embedding type: {type(doc.embedding)}")
            print(f"Embedding length: {len(doc.embedding) if doc.embedding else 0}")
            print(f"Content preview: {doc.content[:200]}...")

if __name__ == "__main__":
    asyncio.run(check_knowledge())
