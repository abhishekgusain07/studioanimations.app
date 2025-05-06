"""Initial database setup for conversations and animations

Revision ID: 0001
Revises: 
Create Date: 2023-10-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), onupdate=sa.text('now()')),
    )
    
    # Create animations table
    op.create_table(
        'animations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('query', sa.Text(), nullable=False),
        sa.Column('generated_code', sa.Text(), nullable=False),
        sa.Column('video_url', sa.String(255), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default=sa.text('1')),
        sa.Column('quality', sa.String(10), nullable=False, server_default=sa.text("'low'")),
        sa.Column('success', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    
    # Create indexes
    op.create_index('idx_animations_user_id', 'animations', ['user_id'])
    op.create_index('idx_animations_conversation_id', 'animations', ['conversation_id'])
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])


def downgrade() -> None:
    # Drop tables
    op.drop_table('animations')
    op.drop_table('conversations') 