# Alembic migration — FT9 Intelligence
# Versão AI9 — Criação da tabela knowledge + extensão pgvector

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import INTEGER, TEXT, VARCHAR

# Revisão
revision = 'knowledge_table_ai9'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Criar extensão pgvector
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    
    # Criar tabela knowledge
    op.create_table(
        'knowledge',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', VARCHAR(255), nullable=False),
        sa.Column('category', VARCHAR(100), nullable=True),
        sa.Column('content', TEXT, nullable=False),
        sa.Column('embedding', sa.dialects.postgresql.VECTOR(dim=1536)),
        sa.Column('organization_id', INTEGER, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    
    # Índice vetorial — similaridade mais rápida
    op.execute("CREATE INDEX knowledge_embedding_idx ON knowledge USING ivfflat (embedding vector_cosine_ops);")

def downgrade():
    op.drop_table('knowledge')
    op.execute("DROP EXTENSION IF EXISTS vector;")
