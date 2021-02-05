# Remove any existing database file first

import pathlib

pathlib.Path("./data/app.db").unlink(missing_ok=True)

# Create database and tables

from models import db, User, Msg

db.connect()
db.create_tables([User, Msg])

# Add sample data

users = [
    {"name": "Serdar"},
    {"name": "Spike"},
    {"name": "Jet"},
    {"name": "Faye"},
    {"name": "Ed"},
]

msgs = [
    {"user": "Serdar", "message": "Hello world."},
    {"user": "Spike", "message": "Just checking in for the first time."},
    {
        "user": "Jet",
        "message": "Has anyone seen Faye or Ed?",
        "replies": [
            {"user": "Faye", "message": "I'm here now!"},
            {"user": "Ed", "message": "Me too!"},
        ],
    },
]


def make_msg(msg, reply_to=None):
    new_msg = Msg.create(user=User.get(name=msg["user"]), message=msg["message"])

    if reply_to:
        new_msg.reply_to = reply_to
        new_msg.save()

    if "replies" in msg:
        for reply in msg["replies"]:
            make_msg(reply, new_msg)

    return new_msg


for user in users:
    User.create(**user)

for msg in msgs:
    new_msg = make_msg(msg)


# Display sample data

for msg in Msg.select():
    print(f'{msg.user.name}: "{msg.message}" {msg.reply_to}')