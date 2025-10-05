"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00

"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('name', sa.String()),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # Projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('ix_projects_user_id', 'projects', ['user_id'])

    # Videos table
    op.create_table(
        'videos',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String()),
        sa.Column('title', sa.String()),
        sa.Column('description', sa.Text()),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('s3_key', sa.String(), nullable=False),
        sa.Column('duration', sa.Float()),
        sa.Column('size_bytes', sa.BigInteger()),
        sa.Column('width', sa.Integer()),
        sa.Column('height', sa.Integer()),
        sa.Column('fps', sa.Float()),
        sa.Column('codec', sa.String()),
        sa.Column('status', sa.String(), nullable=False, default='pending'),
        sa.Column('thumbnail_url', sa.String()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('processed_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='SET NULL')
    )
    op.create_index('ix_videos_user_id', 'videos', ['user_id'])
    op.create_index('ix_videos_status', 'videos', ['status'])

    # Clips table
    op.create_table(
        'clips',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('video_id', sa.String(), nullable=False),
        sa.Column('start_time', sa.Float(), nullable=False),
        sa.Column('end_time', sa.Float(), nullable=False),
        sa.Column('transcript', sa.Text()),
        sa.Column('scene_type', sa.String()),
        sa.Column('thumbnail_url', sa.String()),
        sa.Column('embedding_id', sa.String()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE')
    )
    op.create_index('ix_clips_video_id', 'clips', ['video_id'])

    # Compilations table
    op.create_table(
        'compilations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('status', sa.String(), nullable=False, default='draft'),
        sa.Column('duration', sa.Float()),
        sa.Column('output_url', sa.String()),
        sa.Column('thumbnail_url', sa.String()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('rendered_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('ix_compilations_user_id', 'compilations', ['user_id'])

    # Compilation clips junction table
    op.create_table(
        'compilation_clips',
        sa.Column('compilation_id', sa.String(), nullable=False),
        sa.Column('clip_id', sa.String(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('transition', sa.String()),
        sa.PrimaryKeyConstraint('compilation_id', 'clip_id'),
        sa.ForeignKeyConstraint(['compilation_id'], ['compilations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['clip_id'], ['clips.id'], ondelete='CASCADE')
    )


def downgrade():
    op.drop_table('compilation_clips')
    op.drop_table('compilations')
    op.drop_table('clips')
    op.drop_table('videos')
    op.drop_table('projects')
    op.drop_table('users')
