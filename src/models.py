from peewee import *
from src.configs import root_user_db_pwd
from playhouse.signals import *
from playhouse.pool import PooledMySQLDatabase
import datetime as dt
import logging

logger = logging.getLogger("peewee")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

host = "localhost"

print(root_user_db_pwd)

db = PooledMySQLDatabase("main", host=host, port=3306,
                         user="root", passwd=root_user_db_pwd, max_connections=8, stale_timeout=300)


class BaseModel(Model):
    class Meta:
        database = db


class AbstractModel(BaseModel):
    created_at = DateTimeField(default=dt.datetime.now)
    updated_at = DateTimeField()
    deleted_at = DateTimeField()


# @pre_save(sender=AbstractModel)
# def on_save_handler(model_class, instance: AbstractModel, created):
#     instance.created_at =


class User(AbstractModel):
    first_name = CharField()
    last_name = CharField()
    username = CharField(unique=True, index=True)
    email = CharField(unique=True, index=True)
    pwdhash = CharField()
    pfp_key = CharField()
    cvp_key = CharField()
    headline = CharField(max_length=220)
    bio = TextField()  # limit to 2000 characters


class Post(AbstractModel):
    writer_id = ForeignKeyField(User, backref="posts")
    text_content = TextField()


class Comment(AbstractModel):
    post_id = ForeignKeyField(Post, backref="comments")
    writer_id = ForeignKeyField(User)
    text_content = TextField()
    reply_to = ForeignKeyField('self', backref="reply_to")


def create_tables():
    with db:
        db.create_tables([User, Post, Comment])
