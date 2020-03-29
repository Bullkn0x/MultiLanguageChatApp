from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(session_options={

    'expire_on_commit': False

})

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), nullable=False, unique=True)
    language = db.Column(db.String(32),server_default='english')
    socketID = db.Column(db.String(42)) 
    

class Group(db.Model):
    __tablename__ = 'groups'

    group_id = db.Column(db.Integer, primary_key=True)
    groupname = db.Column(db.String(60), nullable=False, unique=True)
    users = db.relationship('User', secondary='group_users')




t_group_users = db.Table(
    'group_users', db.metadata,
    db.Column('group_id', db.ForeignKey('groups.group_id'), primary_key=True, nullable=False),
    db.Column('user_id', db.ForeignKey('users.user_id'), primary_key=True, nullable=False, index=True)
)


class Message(db.Model):
    __tablename__ = 'messages'
    message_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('users.user_id'), index=True)
    message = db.Column(db.Text)
    user = db.relationship('User')