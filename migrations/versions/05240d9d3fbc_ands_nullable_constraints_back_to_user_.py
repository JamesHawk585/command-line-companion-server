"""Ands nullable constraints back to User class in m models.py

Revision ID: 05240d9d3fbc
Revises: aec1c47d52d1
Create Date: 2024-05-10 14:00:55.131780

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '05240d9d3fbc'
down_revision = 'aec1c47d52d1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('username',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
        batch_op.alter_column('email',
               existing_type=sa.VARCHAR(),
               nullable=False)
        batch_op.alter_column('first_name',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
        batch_op.alter_column('last_name',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
        batch_op.alter_column('_password_hash',
               existing_type=sa.VARCHAR(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('_password_hash',
               existing_type=sa.VARCHAR(),
               nullable=True)
        batch_op.alter_column('last_name',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
        batch_op.alter_column('first_name',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
        batch_op.alter_column('email',
               existing_type=sa.VARCHAR(),
               nullable=True)
        batch_op.alter_column('username',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)

    # ### end Alembic commands ###
