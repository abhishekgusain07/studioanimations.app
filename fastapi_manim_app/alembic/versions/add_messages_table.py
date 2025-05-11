"""Add messages table

Revision ID: 2023_messages_table
Revises: 0001
Create Date: 2023-10-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable


# revision identifiers, used by Alembic.
revision: str = '2023_messages_table'
down_revision: str = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if messagetype already exists - skip enum creation if it does
    conn = op.get_bind()
    result = conn.execute(
        sa.text("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'messagetype')")
    ).scalar()
    
    if not result:
        # Create enum type for message types
        op.execute(sa.DDL("CREATE TYPE messagetype AS ENUM ('user', 'ai')"))
    
    # Check if messages table already exists
    result = conn.execute(
        sa.text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'messages')")
    ).scalar()
    
    if not result:
        # Create messages table
        op.create_table(
            'messages',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('type', sa.Enum('user', 'ai', name='messagetype', create_type=False), nullable=False),
            sa.Column('animation_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
            sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['animation_id'], ['animations.id'], ondelete='SET NULL'),
            sa.Index('ix_messages_conversation_id', 'conversation_id'),
            sa.Index('ix_messages_user_id', 'user_id'),
        )


def downgrade() -> None:
    # Only drop table if it exists
    conn = op.get_bind()
    result = conn.execute(
        sa.text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'messages')")
    ).scalar()
    
    if result:
        op.drop_table('messages')
    
    # Check if messagetype enum is used anywhere else
    enum_used = conn.execute(
        sa.text("""
            SELECT EXISTS (
                SELECT 1 FROM pg_catalog.pg_type t
                JOIN pg_catalog.pg_enum e ON e.enumtypid = t.oid
                WHERE t.typname = 'messagetype'
            )
        """)
    ).scalar()
    
    # Only drop the enum if it exists and is not used elsewhere
    if not enum_used:
        try:
            op.execute(sa.DDL("DROP TYPE IF EXISTS messagetype"))
        except:
            # If drop fails, it might be used by other tables - ignore error
            pass 