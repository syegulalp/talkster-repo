from bottle import route, template, run, request, redirect, response
from models import Msg, User, Token


@route("/")
def main_route():
    user = User.get_user_from_token(request)
    messages = Msg.select().order_by(Msg.date.desc())
    return template("main.html", messages=messages, user=user)


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
