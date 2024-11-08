"""Update products and users table

Revision ID: 0a8bbd6e6726
Revises: 78e91fa8b11c
Create Date: 2024-10-09 16:17:06.714665

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0a8bbd6e6726'
down_revision: Union[str, None] = '78e91fa8b11c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('carts',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('product_id', sa.String(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('products', sa.Column('additional_details', sa.String(), nullable=True))
    op.add_column('products', sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('trousseaus', sa.Column('dimensions', sa.String(), nullable=False))
    op.add_column('trousseaus', sa.Column('child_name', sa.String(), nullable=False))
    op.add_column('trousseaus', sa.Column('custom_date', sa.Date(), nullable=True))
    op.add_column('trousseaus', sa.Column('custom_message', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('trousseaus', 'custom_message')
    op.drop_column('trousseaus', 'custom_date')
    op.drop_column('trousseaus', 'child_name')
    op.drop_column('trousseaus', 'dimensions')
    op.drop_column('products', 'created_at')
    op.drop_column('products', 'additional_details')
    op.drop_table('carts')
    # ### end Alembic commands ###
