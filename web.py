from bottle import route, template, run, request, redirect, response
from models import Msg, User, Token


@route("/")
def main_route():
    user = User.get_user_from_token(request)
    messages = Msg.get_top_level_posts().limit(7)
    return template("main.html", messages=messages, user=user)


@route("/", method="POST")
def main_route_post():
    post_message()
    return main_route()

MSG = Msg.msg_route_prefix

@route(f"{MSG}/<msg_id:int>")
def read_msg(msg_id):
    user = User.get_user_from_token(request)
    msg = Msg.get(id=msg_id)
    return template("read_msg.html", user=user, msg=msg)


@route(f"{MSG}/<msg_id:int>", method="POST")
def post_reply(msg_id):    
    reply = post_message(msg_id)
    return read_msg(msg_id)


def post_message(reply_to=None):
    user = User.get_user_from_token(request)
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


run(port=8000, host="0.0.0.0")
