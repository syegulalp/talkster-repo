from bottle import route, template, run, request, redirect, response
from models import Msg, User, Token

MSG = Msg.msg_route_prefix


def get_user(fn):
    def wrapper(*a, **ka):
        user = User.get_user_from_token(request)
        return fn(user, *a, **ka)

    return wrapper


def login_required(fn):
    def wrapper(user: User, *a, **ka):
        if not user:
            response.status = 401
            return "Not logged in"
        return fn(user, *a, **ka)

    return wrapper


def msg(fn):
    def wrapper(msg_id, *a, **ka):
        msg = Msg.get(id=msg_id)
        if not msg:
            response.status = 404
            return "No such message"
        return fn(msg, *a, **ka)

    return wrapper


@route("/")
@get_user
def main_route(user: User):
    messages = Msg.get_top_level_posts().limit(7)
    return template("main.html", messages=messages, user=user)


@route("/", method="POST")
@get_user
@login_required
def main_route_post(user: User):
    post_message(user)
    return main_route()


@route(f"{MSG}/<msg_id:int>")
@msg
@get_user
def read_msg(user: User, msg: Msg):
    return template("read_msg.html", user=user, msg=msg)


@route(f"{MSG}/<msg_id:int>", method="POST")
@msg
@get_user
@login_required
def post_reply(user: User, msg: Msg):
    reply = post_message(user, reply_to=msg.id)
    return read_msg(msg.id)


def post_message(user: User, reply_to=None):
    if not user:
        response.status = 401
        return "Not logged in"
    return Msg.create(user=user, message=request.forms.post_text, reply_to=reply_to)


@route("/login")
def login_route():
    return template("login.html")


@route("/login", method="POST")
def login_route_post():

    username = request.forms.username
    password = request.forms.password

    try:
        user_login = User.get(name=username, password=User._hash_password(password))
    except User.DoesNotExist:
        user_login = None

    if user_login:
        token: Token = user_login.generate_token()
        response.set_cookie("token", token.id, expires=token.expires)
        return redirect("/")

    message = "User or password not found"

    return template("login.html", message=message)


@route("/delete/<msg_id:int>", method="GET")
@msg
@get_user
@login_required
def delete_message(user: User, msg: Msg):
    return template("delete_msg.html", user=user, msg=msg)


@route("/delete/<msg_id:int>", method="POST")
@msg
@get_user
@login_required
def delete_message_confirm(user: User, msg: Msg):
    if request.forms["msg"] == msg.delete_hash():
        msg.mark_deleted()
        return "Deleted."


run(port=8000, host="0.0.0.0")
