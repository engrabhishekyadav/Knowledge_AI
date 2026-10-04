"""initial_baseline

Revision ID: 442b0ca265e3
Revises: 
Create Date: 2026-09-16 16:55:58.081451

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text
import pgvector.sqlalchemy

# revision identifiers, used by Alembic.
revision: str = '442b0ca265e3'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Idempotent baseline schema creation for PostgreSQL with pgvector."""
    bind = op.get_bind()
    
    # Ensure vector extension exists
    try:
        bind.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    except Exception as ext_err:
        pass

    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    # 1. users table
    if 'users' not in existing_tables:
        op.create_table(
            'users',
            sa.Column('id', sa.String(length=64), nullable=False),
            sa.Column('email', sa.String(length=255), nullable=False),
            sa.Column('full_name', sa.String(length=255), nullable=True),
            sa.Column('hashed_password', sa.String(length=255), nullable=False),
            sa.Column('avatar_url', sa.String(length=512), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
        existing_tables.add('users')

    # 2. notes table
    if 'notes' not in existing_tables:
        op.create_table(
            'notes',
            sa.Column('id', sa.String(length=64), nullable=False),
            sa.Column('user_id', sa.String(length=64), nullable=True),
            sa.Column('title', sa.String(length=255), nullable=False),
            sa.Column('content', sa.Text(), server_default='', nullable=False),
            sa.Column('category', sa.String(length=100), server_default='General', nullable=False),
            sa.Column('tags', sa.JSON(), nullable=True),
            sa.Column('is_favorite', sa.Boolean(), server_default=sa.text('false'), nullable=False),
            sa.Column('embedding', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_notes_title'), 'notes', ['title'], unique=False)
        op.create_index(op.f('ix_notes_category'), 'notes', ['category'], unique=False)
        op.create_index(op.f('ix_notes_user_id'), 'notes', ['user_id'], unique=False)
        existing_tables.add('notes')
    else:
        # Legacy alignment
        notes_indexes = {idx['name'] for idx in inspector.get_indexes('notes')}
        if 'ix_notes_user_id' not in notes_indexes:
            op.create_index(op.f('ix_notes_user_id'), 'notes', ['user_id'], unique=False)

        if 'users' in existing_tables:
            notes_fks = {fk['name'] for fk in inspector.get_foreign_keys('notes')}
            if 'fk_notes_user_id' not in notes_fks:
                try:
                    op.create_foreign_key('fk_notes_user_id', 'notes', 'users', ['user_id'], ['id'], ondelete='CASCADE')
                except Exception:
                    pass

    # 3. tasks table
    if 'tasks' not in existing_tables:
        op.create_table(
            'tasks',
            sa.Column('id', sa.String(length=64), nullable=False),
            sa.Column('user_id', sa.String(length=64), nullable=True),
            sa.Column('title', sa.String(length=255), nullable=False),
            sa.Column('description', sa.Text(), server_default='', nullable=False),
            sa.Column('status', sa.String(length=50), server_default='todo', nullable=False),
            sa.Column('priority', sa.String(length=50), server_default='medium', nullable=False),
            sa.Column('due_date', sa.String(length=50), nullable=True),
            sa.Column('linked_note_id', sa.String(length=64), nullable=True),
            sa.Column('linked_note_title', sa.String(length=255), nullable=True),
            sa.Column('tags', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['linked_note_id'], ['notes.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_tasks_status'), 'tasks', ['status'], unique=False)
        op.create_index(op.f('ix_tasks_priority'), 'tasks', ['priority'], unique=False)
        op.create_index(op.f('ix_tasks_user_id'), 'tasks', ['user_id'], unique=False)
        existing_tables.add('tasks')
    else:
        # Legacy alignment
        tasks_indexes = {idx['name'] for idx in inspector.get_indexes('tasks')}
        if 'ix_tasks_user_id' not in tasks_indexes:
            op.create_index(op.f('ix_tasks_user_id'), 'tasks', ['user_id'], unique=False)

        if 'users' in existing_tables:
            tasks_fks = {fk['name'] for fk in inspector.get_foreign_keys('tasks')}
            if 'fk_tasks_user_id' not in tasks_fks:
                try:
                    op.create_foreign_key('fk_tasks_user_id', 'tasks', 'users', ['user_id'], ['id'], ondelete='CASCADE')
                except Exception:
                    pass

    # 4. chat_messages table
    if 'chat_messages' not in existing_tables:
        op.create_table(
            'chat_messages',
            sa.Column('id', sa.String(length=64), nullable=False),
            sa.Column('sender', sa.String(length=20), nullable=False),
            sa.Column('text', sa.Text(), nullable=False),
            sa.Column('session_id', sa.String(length=100), server_default='default', nullable=False),
            sa.Column('note_id', sa.String(length=64), nullable=True),
            sa.Column('actions', sa.JSON(), nullable=True),
            sa.Column('timestamp_str', sa.String(length=32), nullable=True),
            sa.Column('tokens_used', sa.Integer(), server_default='0', nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_chat_messages_session_id'), 'chat_messages', ['session_id'], unique=False)
        op.create_index(op.f('ix_chat_messages_note_id'), 'chat_messages', ['note_id'], unique=False)
        existing_tables.add('chat_messages')

    # 5. document_chunks table
    if 'document_chunks' not in existing_tables:
        op.create_table(
            'document_chunks',
            sa.Column('id', sa.String(length=64), nullable=False),
            sa.Column('note_id', sa.String(length=64), nullable=False),
            sa.Column('chunk_index', sa.Integer(), server_default='0', nullable=False),
            sa.Column('section', sa.String(length=255), server_default='General', nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('embedding', pgvector.sqlalchemy.Vector(768), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['note_id'], ['notes.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_document_chunks_note_id'), 'document_chunks', ['note_id'], unique=False)
        op.create_index(op.f('ix_document_chunks_chunk_index'), 'document_chunks', ['chunk_index'], unique=False)
        existing_tables.add('document_chunks')
    else:
        # Legacy alignment
        chunk_cols = {c['name']: c for c in inspector.get_columns('document_chunks')}
        if 'embedding' in chunk_cols:
            try:
                op.alter_column(
                    'document_chunks', 'embedding',
                    existing_type=sa.NUMERIC(precision=768),
                    type_=pgvector.sqlalchemy.Vector(dim=768),
                    existing_nullable=True
                )
            except Exception:
                pass


def downgrade() -> None:
    """Downgrade schema in safe reverse dependency order."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if 'document_chunks' in existing_tables:
        op.drop_table('document_chunks')

    if 'chat_messages' in existing_tables:
        op.drop_table('chat_messages')

    if 'tasks' in existing_tables:
        op.drop_table('tasks')

    if 'notes' in existing_tables:
        op.drop_table('notes')

    if 'users' in existing_tables:
        op.drop_table('users')
