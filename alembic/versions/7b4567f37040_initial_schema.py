"""Initial schema

Revision ID: 7b4567f37040
Revises: 
Create Date: 2025-04-11 03:15:13.882252

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b4567f37040'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('industries',
    sa.Column('industry_code', sa.String(length=32), nullable=False),
    sa.Column('name_en', sa.String(length=100), nullable=False),
    sa.Column('name_th', sa.String(length=100), nullable=False),
    sa.Column('description_en', sa.Text(), nullable=True),
    sa.Column('description_th', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('industry_code')
    )
    op.create_table('job_config',
    sa.Column('key', sa.String(), nullable=False),
    sa.Column('value', sa.String(), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('key')
    )
    op.create_index(op.f('ix_job_config_key'), 'job_config', ['key'], unique=False)
    op.create_table('stocks',
    sa.Column('ticker', sa.String(length=20), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('industry_code', sa.String(length=32), nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('modified_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['industry_code'], ['industries.industry_code'], name='fk_stocks_industry_code', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('ticker')
    )
    op.create_index('ix_stocks_industry_active', 'stocks', ['industry_code', 'is_active'], unique=False)
    op.create_table('top_predictions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('industry_code', sa.String(length=32), nullable=False),
    sa.Column('target_date', sa.Date(), nullable=False),
    sa.Column('period', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['industry_code'], ['industries.industry_code'], name='fk_top_prediction_industry'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('industry_code', 'target_date', 'period', name='uq_top_prediction')
    )
    op.create_index('ix_top_predictions_lookup', 'top_predictions', ['industry_code', 'target_date', 'period'], unique=False)
    op.create_table('stock_models',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('stock_ticker', sa.String(length=20), nullable=False),
    sa.Column('version', sa.String(length=50), nullable=False),
    sa.Column('accuracy', sa.Float(), nullable=True),
    sa.Column('model_path', sa.Text(), nullable=False),
    sa.Column('scaler_path', sa.Text(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('features_used', sa.JSON(), nullable=False),
    sa.Column('additional_data', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('modified_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['stock_ticker'], ['stocks.ticker'], name='fk_models_stock', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_stock_models_active', 'stock_models', ['stock_ticker', 'is_active'], unique=False)
    op.create_table('trading_data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('stock_ticker', sa.String(length=20), nullable=False),
    sa.Column('target_date', sa.Date(), nullable=False),
    sa.Column('close', sa.Float(), nullable=False),
    sa.Column('open', sa.Float(), nullable=False),
    sa.Column('high', sa.Float(), nullable=False),
    sa.Column('low', sa.Float(), nullable=False),
    sa.Column('volumes', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['stock_ticker'], ['stocks.ticker'], name='fk_trading_data_stock', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('stock_ticker', 'target_date', name='uq_trading_data')
    )
    op.create_index('ix_trading_data_lookup', 'trading_data', ['stock_ticker', 'target_date'], unique=False)
    op.create_table('predictions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('model_id', sa.Integer(), nullable=False),
    sa.Column('stock_ticker', sa.String(length=20), nullable=False),
    sa.Column('target_date', sa.Date(), nullable=False),
    sa.Column('period', sa.Integer(), nullable=False),
    sa.Column('closing_price', sa.Float(), nullable=True),
    sa.Column('trading_data_id', sa.Integer(), nullable=True),
    sa.Column('predicted_price', sa.Float(), nullable=False),
    sa.Column('rank', sa.Integer(), nullable=True),
    sa.Column('top_prediction_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('modified_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['model_id'], ['stock_models.id'], name='fk_predictions_model', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['stock_ticker'], ['stocks.ticker'], name='fk_predictions_stock', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['top_prediction_id'], ['top_predictions.id'], name='fk_predictions_top'),
    sa.ForeignKeyConstraint(['trading_data_id'], ['trading_data.id'], name='fk_predictions_trading_data', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('stock_ticker', 'model_id', 'target_date', 'period', name='uq_prediction')
    )
    op.create_index('ix_predictions_lookup', 'predictions', ['stock_ticker', 'target_date', 'period'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_predictions_lookup', table_name='predictions')
    op.drop_table('predictions')
    op.drop_index('ix_trading_data_lookup', table_name='trading_data')
    op.drop_table('trading_data')
    op.drop_index('ix_stock_models_active', table_name='stock_models')
    op.drop_table('stock_models')
    op.drop_index('ix_top_predictions_lookup', table_name='top_predictions')
    op.drop_table('top_predictions')
    op.drop_index('ix_stocks_industry_active', table_name='stocks')
    op.drop_table('stocks')
    op.drop_index(op.f('ix_job_config_key'), table_name='job_config')
    op.drop_table('job_config')
    op.drop_table('industries')
    # ### end Alembic commands ###
