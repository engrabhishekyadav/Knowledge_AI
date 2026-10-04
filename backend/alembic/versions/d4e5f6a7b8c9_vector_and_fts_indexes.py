"""vector_and_fts_indexes

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-09-21 00:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text
import pgvector.sqlalchemy

# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, Sequence[str], None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Formalize specialized vector HNSW and full-text search GIN indexes in Alembic."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if 'document_chunks' in existing_tables:
        existing_indexes = {idx['name'] for idx in inspector.get_indexes('document_chunks')}

        # 1. pgvector HNSW Index for sub-millisecond approximate nearest-neighbor search
        if 'ix_document_chunks_embedding_hnsw' not in existing_indexes:
            try:
                bind.execute(text(
                    "CREATE INDEX IF NOT EXISTS ix_document_chunks_embedding_hnsw "
                    "ON document_chunks USING hnsw (embedding vector_cosine_ops);"
                ))
            except Exception as e:
                import logging
                logging.getLogger("alembic").warning(f"HNSW index creation note: {e}")

        # 2. PostgreSQL GIN Index for full-text search
        if 'ix_document_chunks_fts' not in existing_indexes:
            try:
                bind.execute(text(
                    "CREATE INDEX IF NOT EXISTS ix_document_chunks_fts "
                    "ON document_chunks USING gin (to_tsvector('english', content));"
                ))
            except Exception as e:
                import logging
                logging.getLogger("alembic").warning(f"GIN FTS index creation note: {e}")


def downgrade() -> None:
    """Safely drop specialized indexes on rollback."""
    bind = op.get_bind()
    try:
        bind.execute(text("DROP INDEX IF EXISTS ix_document_chunks_fts;"))
        bind.execute(text("DROP INDEX IF EXISTS ix_document_chunks_embedding_hnsw;"))
    except Exception:
        pass
