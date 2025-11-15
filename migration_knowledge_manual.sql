-- ========================================
-- MIGRAÇÃO MANUAL: Tabela Knowledge + pgvector
-- Implementado conforme especificação dos programadores
-- Data: 15/11/2025
-- ========================================

-- 1. Habilitar extensão pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Criar tabela knowledge
CREATE TABLE IF NOT EXISTS knowledge (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    content TEXT NOT NULL,
    embedding vector(1536),  -- Embedding vetorial (1536 dimensões)
    organization_id INTEGER NOT NULL REFERENCES organizations(id),
    source VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 3. Criar índices padrão
CREATE INDEX IF NOT EXISTS ix_knowledge_id ON knowledge(id);
CREATE INDEX IF NOT EXISTS ix_knowledge_title ON knowledge(title);
CREATE INDEX IF NOT EXISTS ix_knowledge_category ON knowledge(category);
CREATE INDEX IF NOT EXISTS ix_knowledge_organization_id ON knowledge(organization_id);

-- 4. Criar índice vetorial HNSW para busca semântica eficiente
-- HNSW = Hierarchical Navigable Small World
-- m = número de conexões por nó (16 é um bom padrão)
-- ef_construction = tamanho da lista de candidatos durante construção (64 é um bom padrão)
CREATE INDEX IF NOT EXISTS knowledge_embedding_hnsw_idx 
ON knowledge 
USING hnsw (embedding vector_l2_ops)
WITH (m = 16, ef_construction = 64);

-- 5. Comentários nas colunas (documentação)
COMMENT ON TABLE knowledge IS 'Base de conhecimento com embeddings vetoriais para RAG';
COMMENT ON COLUMN knowledge.embedding IS 'Embedding vetorial gerado por text-embedding-ada-002 (1536 dimensões)';
COMMENT ON COLUMN knowledge.organization_id IS 'Multi-tenant: cada documento pertence a uma organização';

-- ========================================
-- QUERIES DE TESTE
-- ========================================

-- Verificar se a extensão pgvector está habilitada
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';

-- Verificar se a tabela foi criada
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name = 'knowledge';

-- Verificar índices criados
SELECT indexname, indexdef FROM pg_indexes 
WHERE tablename = 'knowledge';

-- ========================================
-- EXEMPLO DE USO (APÓS POPULAR DADOS)
-- ========================================

-- Buscar por similaridade (distância L2)
-- Substitua [1,2,3,...] pelo embedding real da query
/*
SELECT 
    id, 
    title, 
    content,
    1 - (embedding <=> '[1,2,3,...]'::vector) AS similarity_score
FROM knowledge
WHERE organization_id = 1
  AND is_active = true
ORDER BY embedding <=> '[1,2,3,...]'::vector
LIMIT 5;
*/

-- ========================================
-- ROLLBACK (SE NECESSÁRIO)
-- ========================================

-- Para reverter a migração:
/*
DROP INDEX IF EXISTS knowledge_embedding_hnsw_idx;
DROP INDEX IF EXISTS ix_knowledge_organization_id;
DROP INDEX IF EXISTS ix_knowledge_category;
DROP INDEX IF EXISTS ix_knowledge_title;
DROP INDEX IF EXISTS ix_knowledge_id;
DROP TABLE IF EXISTS knowledge;
-- DROP EXTENSION IF EXISTS vector;  -- Opcional, pode ser mantida
*/
