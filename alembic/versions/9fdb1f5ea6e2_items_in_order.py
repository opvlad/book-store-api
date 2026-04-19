"""items in Order

Revision ID: 9fdb1f5ea6e2
Revises: 501b3b3a591e
Create Date: 2026-04-19 07:42:42.323456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9fdb1f5ea6e2'
down_revision: Union[str, Sequence[str], None] = '501b3b3a591e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('orders', sa.Column('items', postgresql.JSON(astext_type=sa.Text())))

    op.execute(
        """
        UPDATE orders
        SET items = json_build_array(
            json_build_object(
                'book_id', book_id, 'quantity', quantity
            )
        )
        """
    )

    op.alter_column('orders', 'items', nullable=False)
    op.drop_constraint(op.f('orders_book_id_fkey'), 'orders', type_='foreignkey')
    op.drop_column('orders', 'book_id')
    op.drop_column('orders', 'quantity')


def downgrade() -> None:
    op.add_column('orders', sa.Column('book_id', sa.INTEGER()))
    op.add_column('orders', sa.Column('quantity', sa.INTEGER()))

    op.execute(
        """
        UPDATE orders
        SET 
            book_id = (items->0->>'book_id')::integer,
            quantity = (items->0->>'quantity')::integer
        """
    )

    op.create_foreign_key('orders_book_id_fkey', 'orders', 'books', ['book_id'], ['id'])
    op.alter_column('orders', 'book_id', nullable=False)
    op.alter_column('orders', 'quantity', nullable=False)
    op.drop_column('orders', 'items')
