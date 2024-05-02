"""updated relationship

Revision ID: f95cb8939c1c
Revises: 466d19f9a1bf
Create Date: 2024-05-02 16:24:27.534677

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f95cb8939c1c'
down_revision = '466d19f9a1bf'
branch_labels = None
depends_on = None


def upgrade():
    # Drop the conversation_participant table
    # op.drop_table('conversation_participant')
    
    # Add columns to conversation table and create foreign key constraints
    with op.batch_alter_table('conversation', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_1__id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('user_2_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key("fk_conversation_user_1_id", 'user', ['user_1__id'], ['id'])
        batch_op.create_foreign_key("fk_conversation_user_2_id", 'user', ['user_2_id'], ['id'])

    # Add column to message table and create foreign key constraint
    with op.batch_alter_table('message', schema=None) as batch_op:
        batch_op.add_column(sa.Column('conversation', sa.Integer(), nullable=False))
        batch_op.create_foreign_key("fk_message_conversation_id", 'conversation', ['conversation'], ['id'])


def downgrade():
    # Drop foreign key constraints and columns from message and conversation tables
    with op.batch_alter_table('message', schema=None) as batch_op:
        batch_op.drop_constraint("fk_message_conversation_id", type_='foreignkey')
        batch_op.drop_column('conversation')

    with op.batch_alter_table('conversation', schema=None) as batch_op:
        batch_op.drop_constraint("fk_conversation_user_1_id", type_='foreignkey')
        batch_op.drop_constraint("fk_conversation_user_2_id", type_='foreignkey')
        batch_op.drop_column('user_1__id')
        batch_op.drop_column('user_2_id')

    # Recreate the conversation_participant table
    op.create_table(
        
        sa.Column('conversation_id', sa.INTEGER(), nullable=False),
        sa.Column('user_id', sa.INTEGER(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversation.id']),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('conversation_id', 'user_id')
    )
