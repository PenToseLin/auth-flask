"""empty message

Revision ID: 2e1fe5ef8a1c
Revises: 
Create Date: 2019-07-09 17:38:19.932500

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2e1fe5ef8a1c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('auth_ibfk_1', 'auth', type_='foreignkey')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key('auth_ibfk_1', 'auth', 'menu', ['menu_id'], ['id'])
    # ### end Alembic commands ###