"""
發文管理系統資料庫遷移
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_posting_management'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """升級資料庫"""
    
    # 創建發文模板表
    op.create_table('posting_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('trigger_type', sa.String(length=50), nullable=False),
        sa.Column('data_sources', sa.JSON(), nullable=True),
        sa.Column('explainability_config', sa.JSON(), nullable=True),
        sa.Column('news_config', sa.JSON(), nullable=True),
        sa.Column('kol_config', sa.JSON(), nullable=True),
        sa.Column('generation_settings', sa.JSON(), nullable=True),
        sa.Column('tag_settings', sa.JSON(), nullable=True),
        sa.Column('batch_mode_config', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_posting_templates_id'), 'posting_templates', ['id'], unique=False)
    
    # 創建發文會話表
    op.create_table('posting_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_name', sa.String(length=100), nullable=False),
        sa.Column('trigger_type', sa.String(length=50), nullable=False),
        sa.Column('trigger_data', sa.JSON(), nullable=True),
        sa.Column('template_id', sa.Integer(), nullable=True),
        sa.Column('config', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['template_id'], ['posting_templates.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_posting_sessions_id'), 'posting_sessions', ['id'], unique=False)
    
    # 創建發文記錄表
    op.create_table('posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('kol_serial', sa.Integer(), nullable=False),
        sa.Column('kol_nickname', sa.String(length=50), nullable=False),
        sa.Column('kol_persona', sa.String(length=100), nullable=True),
        # KOL資訊
        sa.Column('kol_name', sa.String(length=100), nullable=True),
        sa.Column('kol_style', sa.String(length=50), nullable=True),
        sa.Column('kol_expertise', sa.JSON(), nullable=True),
        sa.Column('kol_question_ratio', sa.Float(), nullable=True),
        sa.Column('kol_content_length', sa.String(length=20), nullable=True),
        
        # 股票資訊
        sa.Column('stock_codes', sa.JSON(), nullable=True),
        sa.Column('stock_names', sa.JSON(), nullable=True),
        sa.Column('stock_data', sa.JSON(), nullable=True),
        sa.Column('stock_analysis_angle', sa.String(length=100), nullable=True),
        sa.Column('stock_technical_signals', sa.JSON(), nullable=True),
        
        # 觸發器資訊
        sa.Column('trigger_type', sa.String(length=50), nullable=True),
        sa.Column('trigger_data', sa.JSON(), nullable=True),
        sa.Column('topic_title', sa.String(length=200), nullable=True),
        sa.Column('topic_keywords', sa.JSON(), nullable=True),
        
        # 生成配置
        sa.Column('generation_config', sa.JSON(), nullable=True),
        sa.Column('data_sources', sa.JSON(), nullable=True),
        sa.Column('explainability_config', sa.JSON(), nullable=True),
        sa.Column('news_config', sa.JSON(), nullable=True),
        sa.Column('news_links', sa.JSON(), nullable=True),
        sa.Column('prompt_template', sa.Text(), nullable=True),
        sa.Column('prompt_template_id', sa.Integer(), nullable=True),
        sa.Column('technical_indicators', sa.JSON(), nullable=True),
        sa.Column('custom_prompt', sa.Text(), nullable=True),
        sa.Column('post_mode', sa.String(length=20), nullable=True),
        sa.Column('content_length', sa.String(length=20), nullable=True),
        sa.Column('content_style', sa.String(length=50), nullable=True),
        sa.Column('max_words', sa.Integer(), nullable=True),
        sa.Column('include_analysis_depth', sa.Boolean(), nullable=True),
        sa.Column('include_charts', sa.Boolean(), nullable=True),
        sa.Column('include_risk_warning', sa.Boolean(), nullable=True),
        sa.Column('tag_settings', sa.JSON(), nullable=True),
        sa.Column('stock_tags', sa.JSON(), nullable=True),
        sa.Column('topic_tags', sa.JSON(), nullable=True),
        
        # 品質檢查
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('ai_detection_score', sa.Float(), nullable=True),
        sa.Column('ai_detection_result', sa.String(length=20), nullable=True),
        sa.Column('risk_level', sa.String(length=20), nullable=True),
        sa.Column('content_quality_issues', sa.JSON(), nullable=True),
        
        # 審核資訊
        sa.Column('reviewer_notes', sa.Text(), nullable=True),
        sa.Column('reviewer_suggestions', sa.Text(), nullable=True),
        sa.Column('approved_by', sa.String(length=50), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('review_status', sa.String(length=20), nullable=True),
        
        # 發布資訊
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('cmoney_post_id', sa.String(length=50), nullable=True),
        sa.Column('cmoney_url', sa.String(length=200), nullable=True),
        sa.Column('publish_error', sa.Text(), nullable=True),
        sa.Column('publish_attempts', sa.Integer(), nullable=True),
        
        # 互動數據
        sa.Column('views', sa.Integer(), nullable=True),
        sa.Column('likes', sa.Integer(), nullable=True),
        sa.Column('comments', sa.Integer(), nullable=True),
        sa.Column('shares', sa.Integer(), nullable=True),
        sa.Column('engagement_rate', sa.Float(), nullable=True),
        sa.Column('interaction_data', sa.JSON(), nullable=True),
        
        # 學習機制數據
        sa.Column('performance_score', sa.Float(), nullable=True),
        sa.Column('learning_feedback', sa.JSON(), nullable=True),
        sa.Column('improvement_suggestions', sa.JSON(), nullable=True),
        
        # 時間戳
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('generated_at', sa.DateTime(), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['posting_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_posts_id'), 'posts', ['id'], unique=False)
    
    # 創建Prompt模板表
    op.create_table('prompt_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('data_source', sa.String(length=50), nullable=False),
        sa.Column('template', sa.Text(), nullable=False),
        sa.Column('variables', sa.JSON(), nullable=True),
        sa.Column('technical_indicators', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prompt_templates_id'), 'prompt_templates', ['id'], unique=False)
    
    # 創建KOL檔案表
    op.create_table('kol_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('serial', sa.Integer(), nullable=False),
        sa.Column('nickname', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('persona', sa.String(length=100), nullable=True),
        sa.Column('style_preference', sa.String(length=50), nullable=True),
        sa.Column('expertise_areas', sa.JSON(), nullable=True),
        sa.Column('activity_level', sa.String(length=20), nullable=True),
        sa.Column('question_ratio', sa.Float(), nullable=True),
        sa.Column('content_length', sa.String(length=20), nullable=True),
        sa.Column('interaction_starters', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('serial')
    )
    op.create_index(op.f('ix_kol_profiles_id'), 'kol_profiles', ['id'], unique=False)
    
    # 創建發文分析表
    op.create_table('posting_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=True),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('views', sa.Integer(), nullable=True),
        sa.Column('likes', sa.Integer(), nullable=True),
        sa.Column('comments', sa.Integer(), nullable=True),
        sa.Column('shares', sa.Integer(), nullable=True),
        sa.Column('engagement_rate', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_posting_analytics_id'), 'posting_analytics', ['id'], unique=False)
    
    # 創建系統配置表
    op.create_table('system_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.JSON(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )
    op.create_index(op.f('ix_system_configs_id'), 'system_configs', ['id'], unique=False)

def downgrade():
    """降級資料庫"""
    op.drop_index(op.f('ix_system_configs_id'), table_name='system_configs')
    op.drop_table('system_configs')
    op.drop_index(op.f('ix_posting_analytics_id'), table_name='posting_analytics')
    op.drop_table('posting_analytics')
    op.drop_index(op.f('ix_kol_profiles_id'), table_name='kol_profiles')
    op.drop_table('kol_profiles')
    op.drop_index(op.f('ix_prompt_templates_id'), table_name='prompt_templates')
    op.drop_table('prompt_templates')
    op.drop_index(op.f('ix_posts_id'), table_name='posts')
    op.drop_table('posts')
    op.drop_index(op.f('ix_posting_sessions_id'), table_name='posting_sessions')
    op.drop_table('posting_sessions')
    op.drop_index(op.f('ix_posting_templates_id'), table_name='posting_templates')
    op.drop_table('posting_templates')
