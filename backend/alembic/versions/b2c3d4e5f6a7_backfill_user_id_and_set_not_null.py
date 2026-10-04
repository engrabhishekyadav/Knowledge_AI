"""backfill_user_id_and_set_not_null

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-09-20 16:40:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    1. Ensure a fallback default user exists.
    2. Backfill existing NULL user_id records in notes, tasks, and chat_messages.
    3. Alter user_id columns on notes, tasks, and chat_messages to NOT NULL safely.
    """
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    # 1. Ensure default system user exists to satisfy foreign key constraints
    if 'users' in existing_tables:
        bind.execute(text(
            "INSERT INTO users (id, email, full_name, hashed_password, created_at, updated_at) "
            "VALUES ('user-demo-admin', 'admin@knowledgeai.internal', 'System Admin', "
            "'$2b$12$e8w.p4yEa5E9b7K6I5Z6xOnj5C5x5N5b5B5c5D5e5F5g5H5i5J5k5', NOW(), NOW()) "
            "ON CONFLICT (id) DO NOTHING;"
        ))

    # 2. Backfill NULL user_id in notes, tasks, and chat_messages
    for table_name in ('notes', 'tasks', 'chat_messages'):
        if table_name in existing_tables:
            cols = {c['name']: c for c in inspector.get_columns(table_name)}
            if 'user_id' in cols:
                bind.execute(text(f"UPDATE {table_name} SET user_id = 'user-demo-admin' WHERE user_id IS NULL;"))
                if cols['user_id'].get('nullable', True):
                    op.alter_column(
                        table_name, 'user_id',
                        existing_type=sa.String(length=64),
                        nullable=False
                    )


def downgrade() -> None:
    """Allow user_id to be nullable again on rollback."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    for table_name in ('chat_messages', 'tasks', 'notes'):
        if table_name in existing_tables:
            cols = {c['name']: c for c in inspector.get_columns(table_name)}
            if 'user_id' in cols and not cols['user_id'].get('nullable', True):
                op.alter_column(
                    table_name, 'user_id',
                    existing_type=sa.String(length=64),
                    nullable=True
                )
