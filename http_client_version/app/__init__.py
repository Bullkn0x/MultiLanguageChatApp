from flask import Flask
from flask_socketio import SocketIO
from flask_session import Session
from .models.mysqldb import db
import os
socketio = SocketIO()



def create_app(debug=False):
    """Create an application."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://chatapp:chatapp@localhost/Chatapp'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    with app.app_context():
        db.create_all()

    socketio.init_app(app)
    return app

