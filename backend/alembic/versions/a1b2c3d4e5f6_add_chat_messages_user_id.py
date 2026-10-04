"""add_chat_messages_user_id

Revision ID: a1b2c3d4e5f6
Revises: 442b0ca265e3
Create Date: 2026-09-17 16:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '442b0ca265e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add user_id column, index, and foreign key to chat_messages table using safe schema inspection."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if 'chat_messages' in existing_tables:
        existing_cols = {col['name'] for col in inspector.get_columns('chat_messages')}
        if 'user_id' not in existing_cols:
            op.add_column('chat_messages', sa.Column('user_id', sa.String(length=64), nullable=True))

        existing_indexes = {idx['name'] for idx in inspector.get_indexes('chat_messages')}
        if 'ix_chat_messages_user_id' not in existing_indexes:
            op.create_index(op.f('ix_chat_messages_user_id'), 'chat_messages', ['user_id'], unique=False)

        if 'users' in existing_tables:
            existing_fks = {fk['name'] for fk in inspector.get_foreign_keys('chat_messages')}
            if 'fk_chat_messages_user_id' not in existing_fks:
                op.create_foreign_key('fk_chat_messages_user_id', 'chat_messages', 'users', ['user_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    """Downgrade schema using safe schema inspection."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if 'chat_messages' in existing_tables:
        existing_fks = {fk['name'] for fk in inspector.get_foreign_keys('chat_messages')}
        if 'fk_chat_messages_user_id' in existing_fks:
            op.drop_constraint('fk_chat_messages_user_id', 'chat_messages', type_='foreignkey')

        existing_indexes = {idx['name'] for idx in inspector.get_indexes('chat_messages')}
        if 'ix_chat_messages_user_id' in existing_indexes:
            op.drop_index(op.f('ix_chat_messages_user_id'), table_name='chat_messages')

        existing_cols = {col['name'] for col in inspector.get_columns('chat_messages')}
        if 'user_id' in existing_cols:
            op.drop_column('chat_messages', 'user_id')
