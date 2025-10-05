"""Add search analytics tables

Revision ID: 002
Revises: 001
Create Date: 2024-01-02 00:00:00

"""
from alembic import op
import sqlalchemy as sa

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Search queries table
    op.create_table(
        'search_queries',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('query_text', sa.Text(), nullable=False),
        sa.Column('results_count', sa.Integer(), default=0),
        sa.Column('processing_time_ms', sa.Float()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('ix_search_queries_user_id', 'search_queries', ['user_id'])
    op.create_index('ix_search_queries_created_at', 'search_queries', ['created_at'])
    
    # Search results table
    op.create_table(
        'search_results',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('search_query_id', sa.String(), nullable=False),
        sa.Column('clip_id', sa.String(), nullable=False),
        sa.Column('rank', sa.Integer(), nullable=False),
        sa.Column('relevance_score', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['search_query_id'], ['search_queries.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['clip_id'], ['clips.id'], ondelete='CASCADE')
    )
    
    # Clip interactions table
    op.create_table(
        'clip_interactions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('clip_id', sa.String(), nullable=False),
        sa.Column('search_query_id', sa.String()),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('duration_seconds', sa.Float()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['clip_id'], ['clips.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['search_query_id'], ['search_queries.id'], ondelete='SET NULL')
    )
    op.create_index('ix_clip_interactions_user_id', 'clip_interactions', ['user_id'])
    op.create_index('ix_clip_interactions_clip_id', 'clip_interactions', ['clip_id'])
    op.create_index('ix_clip_interactions_created_at', 'clip_interactions', ['created_at'])


def downgrade():
    op.drop_table('clip_interactions')
    op.drop_table('search_results')
    op.drop_table('search_queries')
