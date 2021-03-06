"""empty message

Revision ID: b0f5338e6940
Revises: 
Create Date: 2021-08-17 09:38:49.843105

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b0f5338e6940'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admins',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('clinics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('address', sa.Text(), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password', sa.Text(), nullable=False),
    sa.Column('phone', sa.String(length=15), nullable=False),
    sa.Column('picture', sa.Text(), nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.Column('authorized', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('foundations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('address', sa.Text(), nullable=False),
    sa.Column('password', sa.Text(), nullable=False),
    sa.Column('phone', sa.String(length=15), nullable=False),
    sa.Column('picture', sa.Text(), nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.Column('authorized', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('lastname', sa.String(length=50), nullable=False),
    sa.Column('password', sa.Text(), nullable=False),
    sa.Column('phone', sa.String(length=12), nullable=True),
    sa.Column('picture', sa.Text(), nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('doctors',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_clinic', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('lastname', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password', sa.Text(), nullable=False),
    sa.Column('specialty', sa.String(length=50), nullable=False),
    sa.Column('picture', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['id_clinic'], ['clinics.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('pets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('code_chip', sa.String(length=50), nullable=True),
    sa.Column('specie', sa.Enum('cat', 'dog', name='specie'), nullable=False),
    sa.Column('picture', sa.Text(), nullable=True),
    sa.Column('birth_date', sa.Date(), nullable=True),
    sa.Column('breed', sa.String(length=30), nullable=True),
    sa.Column('state', sa.Enum('adoption', 'owned', 'lost', name='pet_state'), nullable=False),
    sa.Column('last_location', sa.Text(), nullable=True),
    sa.Column('id_owner', sa.Integer(), nullable=True),
    sa.Column('id_foundation', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id_foundation'], ['foundations.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id_owner'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('histories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_pet', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id_pet'], ['pets.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('reservation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_clinic', sa.Integer(), nullable=True),
    sa.Column('id_pet', sa.Integer(), nullable=True),
    sa.Column('date_start', sa.DateTime(), nullable=False),
    sa.Column('date_end', sa.DateTime(), nullable=False),
    sa.Column('status', sa.Enum('available', 'reserved', 'canceled', 'confirmed', 'missed', 'finished', name='reservation_status'), nullable=False),
    sa.Column('id_user', sa.Integer(), nullable=True),
    sa.Column('id_doctor', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id_clinic'], ['clinics.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id_doctor'], ['doctors.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id_pet'], ['pets.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id_user'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('diagnostics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_history', sa.Integer(), nullable=True),
    sa.Column('diagnostic', sa.Text(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('doctor_name', sa.String(length=100), nullable=True),
    sa.ForeignKeyConstraint(['id_history'], ['histories.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('surgeries',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_history', sa.Integer(), nullable=True),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('doctor_name', sa.String(length=100), nullable=True),
    sa.Column('date', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['id_history'], ['histories.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('vaccines',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_history', sa.Integer(), nullable=True),
    sa.Column('lot', sa.Text(), nullable=False),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('laboratory', sa.String(length=50), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.ForeignKeyConstraint(['id_history'], ['histories.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('vaccines')
    op.drop_table('surgeries')
    op.drop_table('diagnostics')
    op.drop_table('reservation')
    op.drop_table('histories')
    op.drop_table('pets')
    op.drop_table('doctors')
    op.drop_table('users')
    op.drop_table('foundations')
    op.drop_table('clinics')
    op.drop_table('admins')
    # ### end Alembic commands ###
