"""
Migração Alembic para criar tabela knowledge com suporte a pgvector
Implementado conforme especificação dos programadores - 15/11/2025

Para aplicar esta migração:
1. Copiar este arquivo para alembic/versions/
2. Renomear para: XXXX_add_knowledge_table.py (onde XXXX é o número da revisão)
3. Executar: alembic upgrade head
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import VECTOR

# revision identifiers, used by Alembic.
revision = 'add_knowledge_table'
down_revision = None  # Atualizar com a revisão anterior
branch_labels = None
depends_on = None


def upgrade():
    """
    Criar tabela knowledge com suporte a pgvector
    """
    # 1. Habilitar extensão pgvector
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # 2. Criar tabela knowledge
    op.create_table(
        'knowledge',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', VECTOR(1536), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 3. Criar índices
    op.create_index(op.f('ix_knowledge_id'), 'knowledge', ['id'], unique=False)
    op.create_index(op.f('ix_knowledge_title'), 'knowledge', ['title'], unique=False)
    op.create_index(op.f('ix_knowledge_category'), 'knowledge', ['category'], unique=False)
    op.create_index(op.f('ix_knowledge_organization_id'), 'knowledge', ['organization_id'], unique=False)
    
    # 4. Criar índice vetorial para busca semântica
    # Usando HNSW (Hierarchical Navigable Small World) para performance
    op.execute("""
        CREATE INDEX IF NOT EXISTS knowledge_embedding_hnsw_idx 
        ON knowledge 
        USING hnsw (embedding vector_l2_ops)
        WITH (m = 16, ef_construction = 64)
    """)


def downgrade():
    """
    Reverter migração (remover tabela knowledge)
    """
    # 1. Remover índices
    op.drop_index('knowledge_embedding_hnsw_idx', table_name='knowledge')
    op.drop_index(op.f('ix_knowledge_organization_id'), table_name='knowledge')
    op.drop_index(op.f('ix_knowledge_category'), table_name='knowledge')
    op.drop_index(op.f('ix_knowledge_title'), table_name='knowledge')
    op.drop_index(op.f('ix_knowledge_id'), table_name='knowledge')
    
    # 2. Remover tabela
    op.drop_table('knowledge')
    
    # 3. Remover extensão pgvector (opcional, pode ser mantida)
    # op.execute('DROP EXTENSION IF EXISTS vector')
