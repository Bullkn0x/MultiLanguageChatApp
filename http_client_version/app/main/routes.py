from flask import session, redirect, url_for, render_template, request,make_response
from . import main
from secrets import token_urlsafe
@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method== 'POST':
        username = request.form['username']
        print(username)
    """Login form to enter a room."""
    response = make_response(render_template('index.html'))
    cookie=token_urlsafe(16)
    response.set_cookie('cookie',value=cookie, expires=0)
    return response


