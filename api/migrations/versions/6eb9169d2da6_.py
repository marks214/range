"""empty message

Revision ID: 6eb9169d2da6
Revises: 
Create Date: 2021-02-13 19:22:16.910792

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6eb9169d2da6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('food',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('energy', sa.Float(), nullable=True),
    sa.Column('protein', sa.Float(), nullable=True),
    sa.Column('carbohydrate', sa.Float(), nullable=True),
    sa.Column('fat', sa.Float(), nullable=True),
    sa.Column('fiber', sa.Float(), nullable=True),
    sa.Column('external_id', sa.String(), nullable=True),
    sa.Column('image', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('external_id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('energy_min', sa.Integer(), nullable=True),
    sa.Column('energy_max', sa.Integer(), nullable=True),
    sa.Column('protein_min', sa.Integer(), nullable=True),
    sa.Column('protein_max', sa.Integer(), nullable=True),
    sa.Column('carb_min', sa.Integer(), nullable=True),
    sa.Column('carb_max', sa.Integer(), nullable=True),
    sa.Column('fat_min', sa.Integer(), nullable=True),
    sa.Column('fat_max', sa.Integer(), nullable=True),
    sa.Column('fiber_min', sa.Integer(), nullable=True),
    sa.Column('fiber_max', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('meal',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('food_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('energy', sa.Integer(), nullable=True),
    sa.Column('protein', sa.Integer(), nullable=True),
    sa.Column('carbohydrate', sa.Integer(), nullable=True),
    sa.Column('fat', sa.Integer(), nullable=True),
    sa.Column('fiber', sa.Integer(), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['food_id'], ['food.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('meal')
    op.drop_table('user')
    op.drop_table('food')
    # ### end Alembic commands ###