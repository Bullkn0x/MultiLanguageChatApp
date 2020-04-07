from flask import session, request,Response, redirect, current_app
from flask_socketio import emit, join_room, leave_room, rooms
from .. import socketio
from .utils import try_translate
from ..models.user import User
from .. import mysql
from json import JSONEncoder, dumps
import uuid
import os

# populate room info
conn = mysql.connect()
cursor = conn.cursor()
sql_get_rooms= "SELECT room_id from rooms;"
cursor.execute(sql_get_rooms)
rooms_resp = cursor.fetchall()
cursor.close()

# create dictionary of rooms to track online users
rooms = {res[0]: {} for res in rooms_resp}

num_users=0

def print_user_details(user_id,username,socket_id,join_room):
    print('\nUSER CREDENTIALS')
    print('-'*40)
    print('user id:', user_id)
    print('session username:', username)
    print('socket_id:', socket_id)
    print('joining last chat room_id: ', join_room)
    print('-'*40)
    return 

def print_rooms():
    class MyEncoder(JSONEncoder):
        def default(self, o):
            return o.__dict__ 
    global rooms
    print('\nROOMS:')
    print('-'*40)
    print(dumps(rooms, cls=MyEncoder, indent=4))
    print('-'*40)
    return 

def DB_get_chat_logs(room_id):
    cursor = conn.cursor()

    sql_room_chat = """select u.username, m.message, r.room_name, r.room_id 
                       from messages m join users u on m.user_id = u.user_id 
                       join rooms r on r.room_id =m.room_id where r.room_id = %s;"""
    sql_room_where = (room_id, )
    cursor.execute(sql_room_chat, sql_room_where)
    room_chat_log = [{
        'username':username, 
        'message':message, 
        'room_name' :room_name, 
        'room_id' :room_id } for username, message, room_name, room_id in cursor.fetchall()]

    
    cursor.close()
    return room_chat_log

def DB_insert_msg(user_id, message, room_id):
    
    cursor = conn.cursor()
    sql_message= 'INSERT INTO messages (user_id , message, room_id) VALUES (%s, %s, %s);'
    sql_params = (user_id, message, room_id)
    cursor.execute(sql_message,sql_params)
    conn.commit()
    cursor.close()

def DB_get_user_servers(user_id):
    cursor = conn.cursor()
    sql_server_list = """select r.room_id, r.room_name, r.room_logo_url  
                         from users u 
                         join room_users ru on ru.user_id = u.user_id 
                         join rooms r on ru.room_id = r.room_id 
                         where u.user_id = %s;"""
    sql_server_list_where = (user_id, )
    cursor.execute(sql_server_list, sql_server_list_where)
    
    server_list = [{
        "room_id": room_id, 
        "room_name" : room_name,
        "img_url": img_url 
        } for room_id , room_name, img_url in cursor.fetchall()]
    
    cursor.close()
    return server_list


@socketio.on('connect', namespace='/')
def connect():
    print('USER CONNECTED')
    socket_id = request.sid
    user_id = session['id']
    username = session['user']
    last_room = session['last_room']
    # Get serverlist
    server_list = DB_get_user_servers(user_id)
    # Create user object
    new_user = User(username=username,socket_id=socket_id, current_room=last_room)
    session['user_obj'] = new_user

    # Add user to rooms they subscribe too 
    for server in server_list:
        room_id = server['room_id'] 
        rooms[room_id][username] = new_user
    
    
    print_user_details(user_id,username,socket_id,last_room)
    



    
    print_rooms()

    emit('login', {'username' : username, 'numUsers':len(rooms)})
    cursor = conn.cursor()


    chat_log = DB_get_chat_logs(last_room)
    
    emit('chat log',chat_log)
    emit('server list', server_list)
    emit('user joined', {'username':username, 'numUsers':len(rooms)}, broadcast=True, include_self=False)
   


@socketio.on('join server', namespace='/')
def join_server(data):
    # get chat logs for server
    join_room = int(data['roomID'])
    print(join_room)
    username = data['username']
    session['last_room'] = join_room
    user_obj = session['user_obj']
    user_obj.current_room = join_room
    
    rooms[join_room][username] = user_obj
    print_rooms()
    # get chat logs (list of dictionaries) 
    room_chat_log = DB_get_chat_logs(join_room)
   
    
    cursor= conn.cursor()
    #update user info (current room) 
    sql_update_user_room = "UPDATE  users SET last_room_id = (%s) where username = %s ;"
    sql_room_value = (join_room, username, )
    cursor.execute(sql_update_user_room, sql_room_value)
    conn.commit()
    cursor.close()

    emit('chat log', room_chat_log)


@socketio.on('new message',namespace='/')
def text(msg_data):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    message=msg_data['message']
    sender_name = session.get('user')
    user_id = int(session.get('id'))
    room_id = session['last_room']
    sender =rooms[room_id][sender_name]

    DB_insert_msg(user_id, message, room_id)
    
    # Iterate through rooms and emit messagfasdfe to usersocket 
    for username, receiver in rooms[room_id].items():
        if receiver.current_room == room_id:
            if receiver.language != sender.language:
                print('not same language')
                translated_msg = try_translate(message,sender.language, receiver.language)
                # if successful, transmit
                if translated_msg:
                    message=translated_msg
            # sender renders message to chat using js on enter key, ignore them for now
            
            emit('new message', {'username': sender_name, "message":message}, include_self=False, room=receiver.socket_id)


        # else:
            # emit('notify user', {'username': sender_name, "message":message}, include_self=False, room=receiver.socket_id)

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
    room_id = session['last_room']
    print(room_id)
    for username, receiver in rooms[room_id].items():
        if receiver.current_room == room_id:
            emit('typing', { 'username':session['user'] }, include_self=False, room=receiver.socket_id)

@socketio.on('stop typing',namespace='/')
def user_stopped_typing():
    room_id = session['last_room']
    print(room_id)
    for username, receiver in rooms[room_id].items():
        if receiver.current_room == room_id:
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