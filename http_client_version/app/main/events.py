from flask import session, request,Response, redirect
from flask_socketio import emit, join_room, leave_room, rooms
from .. import socketio
from ..models.mysqldb import db
from .utils import try_translate
from ..models.user import User
from .. import mysql
import json
num_users=0
clients= {}


@socketio.on('connect', namespace='/')
def connect():
    print('IM CONNECTED')
    print('socketid:', request.sid)
    print('session username:',session['user'])
    print('user id', session['id'])
    print(request.cookies)
    socketID = request.sid
    username = session['user']
    new_user = User(username=username,socketID=socketID)
    clients[username]= new_user
    print(clients)

    emit('login', {'username' : username, 'numUsers':len(clients)})
    conn= mysql.connect()
    cursor = conn.cursor()
    sql_chat_log = 'select u.username, m.message from messages m join users u on u.user_id =m.user_id;'
    cursor.execute(sql_chat_log)
    chat_logs = cursor.fetchall()   # convert to dictionary / js object
    chat_logs = [{'username':k, 'message':v} for k,v in chat_logs ]
    emit('chat log',chat_logs)
    emit('user joined', {'username':username, 'numUsers':len(clients)}, broadcast=True, include_self=False)

   


@socketio.on('new message',namespace='/')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session.get('room')
    sender_name = session.get('user')
    user_id = session.get('id')
    sender =clients[sender_name]
    # message_record = Message(message=message)
    conn= mysql.connect()
    cursor = conn.cursor()
    sql_message= 'INSERT INTO messages (user_id , message) VALUES (%s, %s);'
    sql_params = (user_id, message,)
    cursor.execute(sql_message,sql_params)
    conn.commit()
    cursor.close()
    conn.close()
    
    # Iterate through clients and emit messagfasdfe to usersocket 
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

    # db.session.add(message_record)
    # db.session.commit()
    # db.session.close()


@socketio.on('add user',namespace='/')
def login(username):

    print('request cookies',request.cookies)
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    session['user'] = username
    socket=request.sid
    # new_user = User(username=username,socketID=socket)
    clients[username]=new_user

    # user_record =User.query.filter_by(username=username).first()
    

    '''
    Update User Socket Info
    '''
    #Check db to see if user exists
    # if user_record is None:
    #     db.session.add(new_user)
    #     print('new user added')
    # else:
    #     user_record.socketID = socket
    #     print('updated user socket')
    
    # Push new/updated model to database
    # db.session.commit()
    # db.session.close()
    # global num_users
    # num_users+=1

    # # get chat logs
    # chat_record = db.engine.execute("""
    #     SELECT
    #         u.username,
    #         m.message
    #     FROM messages m
    #         JOIN users u ON m.user_id = u.user_id
    # """)
    # from json import dumps
    # chat_log= [{
    #     'username': i['username'],
    #     'message': i['message']
    #     } for i in chat_record]

    # emit('chat log', {'data':chat_log})
    
    emit('login', {'numUsers': num_users})
    emit('user joined', {'username':username, 'numUsers':num_users}, broadcast=True, include_self=False)
    print('username joined:',username)
    for username, obj in clients.items():
        print(obj.__dict__)



@socketio.on('change language',namespace='/')
def update_language(language):
    username = session.get('user')
    user =clients[username]
    user.update_language_pref(language)
    print(user.__dict__)

@socketio.on('typing',namespace='/')
def user_typing():
    emit('typing', { 'username':session['user'] }, broadcast=True, include_self=False)

@socketio.on('stop typing',namespace='/')
def user_stopped_typing():
    emit('stop typing', { 'username':session['user'] }, broadcast=True, include_self=False)

@socketio.on('disconnect',namespace='/' )
def disconnect():
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    # decrease user count
    global num_users
    num_users -= 1
    print(num_users)
    emit('user left', {'username':session['user'], 'numUsers':num_users}, broadcast=True)
    print('client disconnected')

