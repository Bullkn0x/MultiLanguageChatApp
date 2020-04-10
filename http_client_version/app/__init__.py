from flask import Flask
from flask_socketio import SocketIO
from flask_session import Session
from flask_mail import Mail
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor      #For using dictionary cursor
import os
socketio = SocketIO()

mysql = MySQL(cursorclass=DictCursor)
# mysql = MySQL()
mail = Mail()

def create_app(debug=False):
    """Create an application."""
    app = Flask(__name__)
    app.config['FILEDIR'] = 'app/static/_files/'
    app.config['CDN_URL'] = 'http://d1cpyz6yyb1kha.cloudfront.net'
    app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'
    app.config['MYSQL_DATABASE_USER'] = 'anychatdev'
    app.config['MYSQL_DATABASE_PASSWORD'] = 'anychatadmin'
    app.config['MYSQL_DATABASE_DB'] = 'Chatapp'
    app.config['MYSQL_DATABASE_HOST'] = 'anychat.cvjaewaab6rt.us-east-1.rds.amazonaws.com'
    app.config['MYSQL_DATABASE_CHARSET'] = 'utf8mb4'
    app.config.from_pyfile('config.cfg')
    mysql.init_app(app)
    
    mail.init_app(app)
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    socketio.init_app(app)
    return app

