from peewee import (
    CharField,
    DateTimeField,
    DeferredForeignKey,
    ForeignKeyField,
    SqliteDatabase,
    Model,
    TextField,
)

import datetime
import secrets
import settings
import hashlib

db = SqliteDatabase("./data/app.db", pragmas={"journal_mode": "wal"})


class BaseModel(Model):
    class Meta:
        database = db
        SCHEMA_VERSION = 0


class User(BaseModel):
    name = CharField(unique=True, index=True)
    password = TextField(default="")

    @staticmethod
    def _hash_password(password):
        return hashlib.scrypt(
            bytes(password, encoding="utf8"), salt=settings.SITE_KEY, n=16384, r=8, p=1
        ).hex()

    def set_password(self, password):
        self.password = User._hash_password(password)
        self.save()

    def generate_token(self):
        new_token = Token.create(user=self)
        return new_token

    @staticmethod
    def get_user_from_token(request):

        token = request.cookies.token
        if not token:
            return None
        try:
            token = Token.get(id=token)
        except Token.DoesNotExist:
            return None

        if token.expires <= datetime.datetime.now():
            token.delete_instance()
            return None

        return token.user


class Msg(BaseModel):
    user = ForeignKeyField(User, backref="msgs")
    message = TextField()
    date = DateTimeField(default=datetime.datetime.now)
    reply_to = DeferredForeignKey("Msg", null=True)

    msg_route_prefix = "/msg"

    @property
    def link(self):
        return f"{self.msg_route_prefix}/{self.id}"

    @classmethod
    def get_top_level_posts(cls):
        return cls.select().where(cls.reply_to.is_null()).order_by(cls.date.desc())

    def replies(self):
        return Msg.select().where(Msg.reply_to == self).order_by(Msg.date.asc())        

class Token(BaseModel):
    id = TextField(primary_key=True, default=lambda: secrets.token_hex(32))
    user = ForeignKeyField(User, backref="tokens")
    expires = DateTimeField(
        default=lambda: datetime.datetime.now() + datetime.timedelta(days=7), index=True
    )