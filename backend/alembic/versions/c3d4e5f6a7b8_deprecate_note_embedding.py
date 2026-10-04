"""deprecate_note_embedding

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-09-21 00:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Ensure notes.embedding is nullable as chunk embeddings in document_chunks
    serve as the source of truth for pgvector search.
    """
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if 'notes' in existing_tables:
        columns = {col['name'] for col in inspector.get_columns('notes')}
        if 'embedding' in columns:
            op.alter_column('notes', 'embedding', nullable=True)


def downgrade() -> None:
    """Downgrade is a safe no-op."""
    pass
