"""r

Revision ID: 0372defaac0f
Revises: 
Create Date: 2019-02-15 19:19:22.556821

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0372defaac0f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('article', schema=None) as batch_op:
        batch_op.drop_index('ix_article_addtime')

    op.drop_table('article')
    op.drop_table('uprofile')
    op.drop_table('article1')
    with op.batch_alter_table('role', schema=None) as batch_op:
        batch_op.drop_index('uuid')

    op.drop_table('role')
    op.drop_table('userprofile1')
    with op.batch_alter_table('role1', schema=None) as batch_op:
        batch_op.drop_index('email')
        batch_op.drop_index('ix_role1_addtime')
        batch_op.drop_index('username')
        batch_op.drop_index('uuid')

    op.drop_table('role1')
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.drop_index('ix_comments_time')

    op.drop_table('comments')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('comments',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('article_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('user_id', mysql.VARCHAR(length=32), nullable=True),
    sa.Column('body', mysql.VARCHAR(length=200), nullable=True),
    sa.Column('time', mysql.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['article_id'], ['article1.id'], name='comments_ibfk_1'),
    sa.ForeignKeyConstraint(['user_id'], ['role1.uuid'], name='comments_ibfk_2'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.create_index('ix_comments_time', ['time'], unique=False)

    op.create_table('role1',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('uuid', mysql.VARCHAR(length=32), nullable=False),
    sa.Column('username', mysql.VARCHAR(length=80), nullable=False),
    sa.Column('pwd', mysql.VARCHAR(length=80), nullable=False),
    sa.Column('email', mysql.VARCHAR(length=120), nullable=False),
    sa.Column('avatar', mysql.VARCHAR(length=240), nullable=True),
    sa.Column('addtime', mysql.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    with op.batch_alter_table('role1', schema=None) as batch_op:
        batch_op.create_index('uuid', ['uuid'], unique=True)
        batch_op.create_index('username', ['username'], unique=True)
        batch_op.create_index('ix_role1_addtime', ['addtime'], unique=False)
        batch_op.create_index('email', ['email'], unique=True)

    op.create_table('userprofile1',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('user_id', mysql.VARCHAR(length=32), nullable=True),
    sa.Column('nickname', mysql.VARCHAR(length=80), nullable=True),
    sa.Column('gender', mysql.VARCHAR(length=80), nullable=True),
    sa.Column('birthday', sa.DATE(), nullable=True),
    sa.Column('intro', mysql.TEXT(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['role1.uuid'], name='userprofile1_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_table('role',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('uuid', mysql.VARCHAR(length=32), nullable=False),
    sa.Column('username', mysql.VARCHAR(length=80), nullable=False),
    sa.Column('pwd', mysql.VARCHAR(length=80), nullable=False),
    sa.Column('email', mysql.VARCHAR(length=120), nullable=False),
    sa.Column('avatar', mysql.VARCHAR(length=240), nullable=True),
    sa.Column('addtime', mysql.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    with op.batch_alter_table('role', schema=None) as batch_op:
        batch_op.create_index('uuid', ['uuid'], unique=True)

    op.create_table('article1',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('uuid', mysql.VARCHAR(length=32), nullable=False),
    sa.Column('tittle', mysql.VARCHAR(length=128), nullable=False),
    sa.Column('likes', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('collections', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('view', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('img', mysql.VARCHAR(length=240), nullable=True),
    sa.Column('show', mysql.TEXT(), nullable=True),
    sa.Column('body', mysql.TEXT(), nullable=True),
    sa.Column('body_html', mysql.TEXT(), nullable=True),
    sa.Column('addtime', mysql.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['uuid'], ['role1.uuid'], name='article1_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_table('uprofile',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('user_id', mysql.VARCHAR(length=32), nullable=False),
    sa.Column('avatar', mysql.VARCHAR(length=240), nullable=True),
    sa.Column('nickname', mysql.VARCHAR(length=80), nullable=True),
    sa.Column('gender', mysql.VARCHAR(length=80), nullable=True),
    sa.Column('birthday', sa.DATE(), nullable=True),
    sa.Column('intro', mysql.TEXT(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['role.uuid'], name='uprofile_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_table('article',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('uuid', mysql.VARCHAR(length=32), nullable=False),
    sa.Column('tittle', mysql.VARCHAR(length=128), nullable=False),
    sa.Column('likes', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('collections', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('view', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('show', mysql.TEXT(), nullable=True),
    sa.Column('body', mysql.TEXT(), nullable=True),
    sa.Column('body_html', mysql.TEXT(), nullable=True),
    sa.Column('addtime', mysql.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['uuid'], ['role.uuid'], name='article_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    with op.batch_alter_table('article', schema=None) as batch_op:
        batch_op.create_index('ix_article_addtime', ['addtime'], unique=False)

    # ### end Alembic commands ###
