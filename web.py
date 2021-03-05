from bottle import route, template, run
from models import Msg

@route('/')
def main_route():
    messages = Msg.select().order_by(Msg.date.desc())
    return template('main.html', messages=messages)

run(port=8000, host="0.0.0.0")