from flask import session, redirect, url_for, render_template, request,make_response,send_file
from flask_mail import Message
from . import main
from secrets import token_urlsafe
from .. import mysql, mail
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from werkzeug.security import generate_password_hash as hash_pass, check_password_hash as check_pass
import random
import string

global COOKIE_TIME_OUT
COOKIE_TIME_OUT = 60*60*24

#CHANGE FOR PRODUCTION
s = URLSafeTimedSerializer('thisisasecret')



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
    if 'u_id' in request.cookies:
        username = request.cookies.get('u_id')
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
        sql = 'SELECT * FROM users WHERE email=%s or username=%s'
        # prevent sql injection
        sql_where = (email_or_username, email_or_username, )
        # execute query
        cursor.execute(sql, sql_where)
        db_user = cursor.fetchone()
        cursor.close()
        if db_user and check_pass(db_user['password'], password):
            session['user'] = db_user['username']   #put username in session
            session['id'] = db_user['user_id']
            session['last_room'] =db_user['last_room_id']
            resp = make_response(redirect('/'))
            # cookieid= token_urlsafe(16)
            if remember:
                resp.set_cookie('u_id',db_user['username'], max_age=COOKIE_TIME_OUT,expires=COOKIE_TIME_OUT)
                resp.set_cookie('pwd',password, max_age=COOKIE_TIME_OUT, expires=COOKIE_TIME_OUT)
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

@main.route('/forgetpassword', methods=['GET', 'POST'] )
def forgetpassword():
    conn=None
    cursor = None
    error = None

    if request.method == 'POST':
        # get form data
        email= request.form['email']
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = 'SELECT * FROM users WHERE email=%s'
        # prevent sql injection
        sql_where = (email)
        # execute query
        cursor.execute(sql, sql_where)
        db_user = cursor.fetchone()
        print('db user')
        print(db_user)

        if db_user:
            # session['user'] = db_user[1]   #put username in session
            # session['id'] = db_user[0]
            username=db_user['username']
            email = db_user['email']
            updatequery='UPDATE users SET password=%s WHERE user_id=%s'
            generated_password = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(10))
            
            sql_update=(hash_pass(generated_password,method='sha256'), db_user['user_id'],)
            print('generated password: '+ generated_password)
            cursor.execute(updatequery,sql_update)
            conn.commit()
            cursor.close()

            # token = s.dumps(email, salt='email-confirm')

            msg = Message(subject='Password Reset Confirmation', sender='anychatio@gmail.com', recipients=[email])

            # link = url_for('.confirm_email', token=token, external=True)

            msg.html = render_template('passwordresetconfirmation.html', generated_password=generated_password, username=username)
            mail.send(msg)
            return render_template('redirect.html', error=error)
            
        else:
            error = 'Invalid Email! Please try again.'
            print(error)
            return render_template('forgetpassword.html', error=error)
        
    return render_template('forgetpassword.html', error=error)

@main.route('/test', methods=['GET', 'POST'] )
def test():
    return render_template('confirmationEmail.html')

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
        sql_values = (username, email, hash_pass(password,method='sha256'),)
        cursor.execute(add_user, sql_values)
        conn.commit()
        cursor.close()

        #Create token for email confirmation from serializer
        
        token = s.dumps(email, salt='email-confirm')
    
        msg = Message(subject='Confirm Your Email', sender='anychatio@gmail.com', recipients=[email])

        link = 'http://localhost:8000'+url_for('main.confirm_email', token=token, external=True)
        print(link)
        msg.body = f'Your link is <h6>HERE</h6> {link}'
        msg.html = render_template('confirmationEmail.html', username=username, link=link)
        mail.send(msg)
        return render_template('redirect.html', error=error)
        # return redirect('/')

    return render_template('signup.html', error=error)

@main.route('/profilesettings', methods=['GET', 'POST'] )
def profilesettings():

    return render_template('profilesettings.html')

@main.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=60)
        conn=mysql.connect()
        cursor = conn.cursor()
        sql_activate_user = 'CALL ACTIVATE_USER(%s);'
        sql_where= (email,)
        cursor.execute(sql_activate_user, sql_where)
        conn.commit()
        success='Email Verified! Please login!'
        cursor.close()
        
    except SignatureExpired:
        return 'Token Expired'

    return render_template('landing.html', success=success)


@main.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'session' in request.cookies:
        pass
        # print('FOUND SESSION COOKIES', request.cookies.get('session'))
        # print(request.cookies)
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


@main.route('/download', methods=['GET'])
def download(fileinfo='file i need'):
    return send_file('/home/bullkn0x/Documents/Python/ChatApp/V1/http_client_version/app/static/_files/5795c17a4ba643d5ae7b0a56c098d690.csv',
    as_attachment=True, attachment_filename='hello.csv')
