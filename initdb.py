# Remove any existing database file first

import pathlib

pathlib.Path("./data/app.db").unlink(missing_ok=True)

# Create database and tables

from models import db, User, Msg, Token

db.connect()
db.create_tables([User, Msg, Token])

# Add sample data

users = [
    {"name": "Serdar", "password": "motoko1995"},
    {"name": "Spike", "password": "bandai1998"},
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
    {
        "user": "Serdar",
        "message": "Does 'Voltswagen' count as an April Fuel's joke?",
        "replies": [
            {"user": "Faye", "message": "Boo!! 🍅🍅🍅"},
            {"user": "Ed", "message": "That's the worst one yet."},
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
    new_user = User.create(**user)
    new_user.set_password(user.get("password", "vicious1998"))

for msg in msgs:
    new_msg = make_msg(msg)


# Display sample data

for msg in Msg.select():
    print(f'{msg.user.name}: "{msg.message}" {msg.reply_to}')
