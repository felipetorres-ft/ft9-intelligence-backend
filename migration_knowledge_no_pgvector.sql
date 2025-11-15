-- ============================================
-- MIGRAÇÃO KNOWLEDGE BASE - SEM PGVECTOR
-- Versão alternativa usando TEXT para embeddings
-- Data: 15/11/2025
-- ============================================

-- Criar tabela knowledge
CREATE TABLE IF NOT EXISTS knowledge (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    embedding_json TEXT,  -- Armazena embedding como JSON string
    metadata JSONB DEFAULT '{}',
    source VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar índices para performance
CREATE INDEX IF NOT EXISTS idx_knowledge_org ON knowledge(organization_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_title ON knowledge(title);
CREATE INDEX IF NOT EXISTS idx_knowledge_source ON knowledge(source);
CREATE INDEX IF NOT EXISTS idx_knowledge_created ON knowledge(created_at DESC);

-- Criar índice GIN para busca em metadata JSONB
CREATE INDEX IF NOT EXISTS idx_knowledge_metadata ON knowledge USING GIN(metadata);

-- Verificar estrutura criada
SELECT 
    table_name, 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns
WHERE table_name = 'knowledge'
ORDER BY ordinal_position;

-- Verificar índices criados
SELECT 
    indexname, 
    indexdef
FROM pg_indexes
WHERE tablename = 'knowledge';

-- NOTA IMPORTANTE:
-- Esta migração usa TEXT para armazenar embeddings como JSON string
-- Para busca semântica real com pgvector, será necessário:
-- 1. Usar um banco PostgreSQL com extensão pgvector instalada
-- 2. Executar migration_knowledge_manual.sql ao invés deste arquivo
-- 3. Ou usar um serviço externo como Pinecone/Weaviate para vetores
