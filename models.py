from peewee import CharField, DateTimeField, DeferredForeignKey, ForeignKeyField, SqliteDatabase, Model, TextField
import datetime

db = SqliteDatabase('./data/app.db', pragmas = {"journal_mode":"wal"})

class BaseModel(Model):
    class Meta:
        database = db
        SCHEMA_VERSION = 0

class User(BaseModel):
    name = CharField(unique=True, index=True)

class Msg(BaseModel):
    user = ForeignKeyField(User, backref='msgs')
    message = TextField()
    date = DateTimeField(default = datetime.datetime.now)
    reply_to = DeferredForeignKey("Msg", null=True)