"""align_model_fields

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-09-21 01:25:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, Sequence[str], None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Align model fields, foreign keys, and indexes across users, tasks, and chat_messages."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    # 1. users.avatar_url
    if 'users' in existing_tables:
        user_columns = {col['name'] for col in inspector.get_columns('users')}
        if 'avatar_url' not in user_columns:
            op.add_column('users', sa.Column('avatar_url', sa.String(length=512), nullable=True))

    # 2. tasks: foreign key on linked_note_id and index on priority
    if 'tasks' in existing_tables:
        task_columns = {col['name'] for col in inspector.get_columns('tasks')}
        task_indexes = {idx['name'] for idx in inspector.get_indexes('tasks')}
        task_fks = {fk['name'] for fk in inspector.get_foreign_keys('tasks')}

        # Index on priority
        if 'ix_tasks_priority' not in task_indexes:
            try:
                op.create_index('ix_tasks_priority', 'tasks', ['priority'], unique=False)
            except Exception:
                pass

        # Foreign key on linked_note_id -> notes.id
        if 'notes' in existing_tables and 'linked_note_id' in task_columns:
            if 'fk_tasks_linked_note_id' not in task_fks:
                try:
                    op.create_foreign_key(
                        'fk_tasks_linked_note_id',
                        'tasks', 'notes',
                        ['linked_note_id'], ['id'],
                        ondelete='SET NULL'
                    )
                except Exception:
                    pass

    # 3. chat_messages: note_id, actions, timestamp_str
    if 'chat_messages' in existing_tables:
        chat_columns = {col['name'] for col in inspector.get_columns('chat_messages')}
        chat_indexes = {idx['name'] for idx in inspector.get_indexes('chat_messages')}

        if 'note_id' not in chat_columns:
            op.add_column('chat_messages', sa.Column('note_id', sa.String(length=64), nullable=True))

        if 'ix_chat_messages_note_id' not in chat_indexes:
            try:
                op.create_index('ix_chat_messages_note_id', 'chat_messages', ['note_id'], unique=False)
            except Exception:
                pass

        if 'actions' not in chat_columns:
            op.add_column('chat_messages', sa.Column('actions', sa.JSON(), nullable=True))

        if 'timestamp_str' not in chat_columns:
            op.add_column('chat_messages', sa.Column('timestamp_str', sa.String(length=32), nullable=True))


def downgrade() -> None:
    """Revert aligned fields and indexes in reverse order."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    # 1. chat_messages
    if 'chat_messages' in existing_tables:
        chat_columns = {col['name'] for col in inspector.get_columns('chat_messages')}
        chat_indexes = {idx['name'] for idx in inspector.get_indexes('chat_messages')}

        if 'ix_chat_messages_note_id' in chat_indexes:
            op.drop_index('ix_chat_messages_note_id', table_name='chat_messages')

        if 'timestamp_str' in chat_columns:
            op.drop_column('chat_messages', 'timestamp_str')

        if 'actions' in chat_columns:
            op.drop_column('chat_messages', 'actions')

        if 'note_id' in chat_columns:
            op.drop_column('chat_messages', 'note_id')

    # 2. tasks
    if 'tasks' in existing_tables:
        task_indexes = {idx['name'] for idx in inspector.get_indexes('tasks')}
        task_fks = {fk['name'] for fk in inspector.get_foreign_keys('tasks')}

        if 'fk_tasks_linked_note_id' in task_fks:
            op.drop_constraint('fk_tasks_linked_note_id', 'tasks', type_='foreignkey')

        if 'ix_tasks_priority' in task_indexes:
            op.drop_index('ix_tasks_priority', table_name='tasks')

    # 3. users
    if 'users' in existing_tables:
        user_columns = {col['name'] for col in inspector.get_columns('users')}
        if 'avatar_url' in user_columns:
            op.drop_column('users', 'avatar_url')
