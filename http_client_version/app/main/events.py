from flask import session, request
from flask_socketio import emit, join_room, leave_room
from .. import socketio
from ..models.user import User, db


@socketio.on('joined', namespace='/')
def joined(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    
    join_room(room)
    emit('status', {'msg': session.get('name') + ' has entered the room.'}, room=room)
@socketio.on('new message', namespace='/')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session.get('room')
    sender = session.get('user')
    print(sender)
    # send to all users, but sender since sender is rendering to page using js
    emit('new message', {'username': sender, "message":message}, broadcast=True, include_self=False)

@socketio.on('add user', namespace='/')
def login(username):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    session['user'] = username
    new_user = User(username=username)
    db.session.add(new_user)
    db.session.commit()
    emit('login', {'numUsers': 5})
    emit('user joined', {'username':username, 'numUsers':5}, broadcast=True)

    print(username)

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
    # add user count
    emit('user left', {'username':session['user'], 'numUsers':5}, broadcast=True)
    print('client disconnected')

