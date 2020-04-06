from flask import session, request,Response, redirect
from flask_socketio import emit, join_room, leave_room, rooms
from .. import socketio
from .utils import try_translate
from ..models.user import User
from .. import mysql
import json
num_users=0
rooms= {}


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
    rooms[username]= new_user
    print(rooms)




    emit('login', {'username' : username, 'numUsers':len(rooms)})
    conn= mysql.connect()
    cursor = conn.cursor()


    sql_chat_log = """select u.username, m.message 
                      from messages m join users u on u.user_id =m.user_id;"""
    cursor.execute(sql_chat_log)
    chat_logs = cursor.fetchall()   # convert to dictionary / js object
    chat_logs = [{'username':k, 'message':v, "room_name": "Global Chat"} for k,v in chat_logs ]
    
    # Get servlist
    sql_server_list = """select g.room_id, g.room_name, room_logo_url  
                         from users u join group_users gu on gu.user_id = u.user_id 
                         join groups g on gu.room_id = g.room_id 
                         where u.username = %s;"""
    sql_server_list_where = (username, )
    cursor.execute(sql_server_list, sql_server_list_where)
    
    server_list = [{
        "room_id": room_id, 
        "room_name" : room_name,
        "img_url": img_url 
        } for room_id , room_name, img_url in cursor.fetchall()]
    print(server_list)
    
    emit('chat log',chat_logs)
    emit('server list', server_list)
    emit('user joined', {'username':username, 'numUsers':len(rooms)}, broadcast=True, include_self=False)
   


@socketio.on('join server', namespace='/')
def join_server(data):
    # get chat logs for server
    join_room = data['roomID']
    username = data['username']
    print(data)
    conn= mysql.connect()
    cursor = conn.cursor()
    sql_room_chat = """select u.username, m.message, g.room_name 
                       from messages m join users u on m.user_id = u.user_id 
                       join groups g on g.room_id =m.room_id where g.room_id = %s;"""

    sql_room_where = (join_room, )
    cursor.execute(sql_room_chat, sql_room_where)
    room_chat_log = [{'username':username, 'message':message, 'room_name' :room_id} for username, message, room_id in cursor.fetchall()]
    
    #update user info (current room) 
    sql_update_user_room = "UPDATE  users SET last_room_id = (%s) where username = %s ;"
    sql_room_value = (join_room, username, )
    cursor.execute(sql_update_user_room, sql_room_value)
    conn.commit()
    cursor.close()

    emit('chat log', room_chat_log)
    print(room_chat_log)
@socketio.on('new message',namespace='/')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    print('room is')
    
    room = session.get('room')
    sender_name = session.get('user')
    user_id = session.get('id')
    sender =rooms[sender_name]
    # message_record = Message(message=message)
    conn= mysql.connect()
    cursor = conn.cursor()
    sql_message= 'INSERT INTO messages (user_id , message) VALUES (%s, %s);'
    sql_params = (user_id, message,)
    cursor.execute(sql_message,sql_params)
    conn.commit()
    cursor.close()
    conn.close()
    
    # Iterate through rooms and emit messagfasdfe to usersocket 
    for username, receiver in rooms.items():
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





@socketio.on('change language',namespace='/')
def update_language(language):
    username = session.get('user')
    user =rooms[username]
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
    """Sent by rooms when they leave a room.
    A status message is broadcast to all people in the room."""
    # decrease user count
    global num_users
    num_users -= 1
    print(num_users)
    emit('user left', {'username':session['user'], 'numUsers':num_users}, broadcast=True)
    print('client disconnected')


import uuid
from flask import current_app
import os
@socketio.on('start-transfer', namespace='/')
def start_transfer(filename, size):
    """Process an upload request from the client."""
    _, ext = os.path.splitext(filename)
    if ext in ['.exe', '.bin', '.js', '.sh', '.py', '.php']:
        return False  # reject the upload

    id = uuid.uuid4().hex  # server-side filename
    print(id)
    with open(current_app.config['FILEDIR'] + id + '.json', 'wt') as f:
        json.dump({'filename': filename, 'size': size}, f)
    with open(current_app.config['FILEDIR'] + id + ext, 'wb') as f:
        pass
    return id + ext  # allow the upload


@socketio.on('write-chunk', namespace='/')
def write_chunk(filename, offset, data):
    """Write a chunk of data sent by the client."""
    if not os.path.exists(current_app.config['FILEDIR'] + filename):
        return False
    try:
        with open(current_app.config['FILEDIR'] + filename, 'r+b') as f:
            f.seek(offset)
            f.write(data)
    except IOError:
        return False
    return True