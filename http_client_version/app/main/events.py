from flask import session, request,Response
from flask_socketio import emit, join_room, leave_room, rooms
from .. import socketio
from ..models.mysqldb import db
from .utils import try_translate
from ..models.mysqldb import User, Message

num_users=0
clients= {}



@socketio.on('new message', namespace='/')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session.get('room')
    sender_name = session.get('user')
    sender =clients[sender_name]
    message_record = Message(message=message)
    # Iterate through clients and emit message to usersocket 
    for username, receiver in clients.items():
        if receiver.language != sender.language:
            print('not same language')
            translated_msg = try_translate(message,sender.language, receiver.language)
            # if successful, transmit
            if translated_msg:
                message=translated_msg
        # sender renders message to chat using js on enter key, ignore them for now
        if receiver.socketID != sender.socketID:
            emit('new message', {'username': sender_name, "message":message}, room=receiver.socketID)

    db.session.add(message_record)
    db.session.commit()
@socketio.on('add user', namespace='/')
def login(username):

    print('request cookies',request.cookies)
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    session['user'] = username
    socket=request.sid
    new_user = User(username=username,socketID=socket)
    clients[username]=new_user

    user_record =User.query.filter_by(username=username).first()
    

    '''
    Update User Socket Info
    '''
    #Check db to see if user exists
    if user_record is None:
        db.session.add(new_user)
        print('new user added')
    else:
        user_record.socketID = socket
        print('updated user socket')
    
    # Push new/updated model to database
    db.session.commit()

    global num_users
    num_users+=1
    emit('login', {'numUsers': num_users})
    emit('user joined', {'username':username, 'numUsers':num_users}, broadcast=True, include_self=False)
    print('username joined:',username)
    for username, obj in clients.items():
        print(obj.__dict__)


@socketio.on('change language', namespace='/')
def update_language(language):
    username = session.get('user')
    user =clients[username]
    user.update_language_pref(language)
    print(user.__dict__)

@socketio.on('typing', namespace='/')
def user_typing():
    emit('typing', { 'username':session['user'] }, broadcast=True, include_self=False)

@socketio.on('stop typing', namespace='/')
def user_stopped_typing():
    emit('stop typing', { 'username':session['user'] }, broadcast=True, include_self=False)

@socketio.on('disconnect', namespace='/' )
def disconnect():
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    # decrease user count
    global num_users
    num_users -= 1
    print(num_users)
    emit('user left', {'username':session['user'], 'numUsers':num_users}, broadcast=True)
    print('client disconnected')

