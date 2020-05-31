"""empty message

Revision ID: 18aa6c0f7b29
Revises: 
Create Date: 2020-05-30 14:02:24.839049

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '18aa6c0f7b29'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('board_members_ibfk_1', 'board_members', type_='foreignkey')
    op.create_foreign_key(None, 'board_members', 'boards', ['boardId'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'board_members', type_='foreignkey')
    op.create_foreign_key('board_members_ibfk_1', 'board_members', 'cards', ['boardId'], ['id'])
    # ### end Alembic commands ###
