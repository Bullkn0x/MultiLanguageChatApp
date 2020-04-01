from flask import session, redirect, url_for, render_template, request,make_response
from . import main
from secrets import token_urlsafe
from .. import mysql


global COOKIE_TIME_OUT
COOKIE_TIME_OUT = 60*60*24 

@main.route('/', methods=['GET'])
def home():
    if 'user' in session:
        username = session['user']
        return render_template('landing.html', signed_in = True, username=username)
    return render_template('landing.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    conn=None
    cursor = None
    error = None
    if 'user' in request.cookies:
        username = request.cookies.get('user')
        password = request.cookies.get('pwd')
        session['user'] = username
        return redirect('/')

    
    if request.method == 'POST':
        # get form data
        email_or_username = request.form['email']
        password = request.form['password']
        remember = request.form.getlist('remember')
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = 'SELECT * FROM users WHERE email=%s or username=%s AND password=%s'
        # prevent sql injection
        sql_where = (email_or_username, email_or_username, password, )
        # execute query
        cursor.execute(sql, sql_where)
        db_user = cursor.fetchone()

        if db_user and password == db_user[5]:
            session['user'] = db_user[1]   #put username in session
            session['id'] = db_user[0]
            conn.close()
            resp = make_response(render_template('landing.html', signed_in=True, username=db_user[1]))
            # cookieid= token_urlsafe(16)
            print(remember)
            if remember:
                resp.set_cookie('user',db_user[1], max_age=COOKIE_TIME_OUT,expires=COOKIE_TIME_OUT)
                resp.set_cookie('password',password, max_age=COOKIE_TIME_OUT, expires=COOKIE_TIME_OUT)
                resp.set_cookie('rem', 'yes',  max_age=COOKIE_TIME_OUT,expires=COOKIE_TIME_OUT)
            return resp
        else:            
            error = 'Invalid Credentials. Please try again.'
            print(error)
    return render_template('login.html', error=error)

@main.route('/logout')
def logout():
	if 'user' in session:
		session.pop('user', None)
	return redirect('/')

@main.route('/signup', methods=['GET', 'POST'] )
def signup():
    error = None 
    conn= None
    cursor = None
    if request.method == 'POST':
        # get form data
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        conn = mysql.connect()
        cursor = conn.cursor()
        check_user = 'SELECT * FROM users WHERE email=%s or username=%s;'
        sql_where = (email, username,)
        cursor.execute(check_user, sql_where)
        db_user = cursor.fetchone()
        if db_user:
            error="User already exists"
            return render_template('signup.html', error=error)
        
        add_user= 'INSERT INTO users (username, email, password) VALUES (%s, %s, %s);'
        sql_values = (username, email, password,)
        cursor.execute(add_user, sql_values)
        conn.commit()
        cursor.close()
        conn.close()
        session['user'] = username

        return redirect('/')
    
    return render_template('signup.html', error=error)
        

@main.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'session' in request.cookies:
        print('FOUND SESSION COOKIES', request.cookies.get('session'))
        print(request.cookies)
    else:
        return redirect('/login')

    if request.method== 'POST':
        username = request.form['username']
        print(username)
    """Login form to enter a room."""
    response = make_response(render_template('chat.html'))
    cookie=token_urlsafe(16)
    response.set_cookie('cookie',value=cookie, expires=0)
    return response


