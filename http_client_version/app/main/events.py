from flask import session, request,Response, redirect, current_app
from flask_socketio import emit, join_room, leave_room, rooms
from .. import socketio
from .utils import try_translate
from .awsHelper import upload_file
from ..models.user import User
from .. import mysql
from json import JSONEncoder, dumps, dump
import uuid
import os
# populate room info
conn = mysql.connect()
cursor = conn.cursor()
sql_get_rooms= "SELECT room_id from rooms;"
cursor.execute(sql_get_rooms)
rooms_resp = cursor.fetchall()
cursor.close()
print(rooms_resp)
# create dictionary of rooms to track online users
rooms = {row['room_id']: {} for row in rooms_resp}
print(rooms)
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
    room_chat_log = cursor.fetchall()

    
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
    
    server_list = cursor.fetchall()
    cursor.close()
    return server_list

def DB_get_server_users(room_id):
    cursor = conn.cursor()
    sql_server_users = """select
                            DISTINCT (u.user_id),
                            u.username 
                        from
                        rooms r 
                        join room_users ru on
                            ru.room_id = r.room_id
                        join users u on ru.user_id = u.user_id and 
                            r.room_id = %s;"""
    sql_where = (room_id, )
    cursor.execute(sql_server_users, sql_where)

    server_users = cursor.fetchall()
    cursor.close()

    return server_users

def DB_get_public_servers(search_term=None):
    cursor = conn.cursor()
    if search_term:
        SQL_GET_SERVERS = """SELECT          
                                room_id, room_name, room_logo_url
                            FROM 
                                rooms
                            WHERE room_name LIKE %s;
                          """
        sql_where= f'%{search_term}%'
    else:
        SQL_GET_SERVERS = """SELECT
                         room_id, room_name, room_logo_url
                         FROM 
                         rooms
                         where public_access = True and room_id > 1 ;
                        """
        sql_where = None
    cursor.execute(SQL_GET_SERVERS, sql_where)
    public_servers = cursor.fetchall()
    cursor.close()

    return public_servers

def DB_get_user_info(user_id):
    cursor = conn.cursor()

    SQL_GET_USER = """SELECT * FROM users
                         WHERE user_id = %s;
                        """
    cursor.execute(SQL_GET_USER, user_id)
    user_info = cursor.fetchone()
    
    return user_info

def DB_insert_private_msg(from_user, to_user, message):
    cursor = conn.cursor()

    SQL_PRIVATE_MESSAGE = 'INSERT INTO private_messages (to_user , from_user, message) VALUES (%s, %s, %s);'
    sql_values = (from_user, to_user, message, )
    cursor.execute(SQL_PRIVATE_MESSAGE, sql_values)
    conn.commit()
    cursor.close()


def DB_get_pm_chat_log(me, them):
    cursor = conn.cursor()
    SQL_GET_PRIVATE_MESSAGE_LOG = """select to_user, from_user,
                                     message, from_user = %s 'mymsg' from 
                                    ( select * from private_messages pm where to_user in (%s, %s)) as sub 
                                    where from_user in (%s, %s)"""
    sql_where = (me, me, them, me, them, )
    cursor.execute(SQL_GET_PRIVATE_MESSAGE_LOG, sql_where)
    pm_chat_log = cursor.fetchall()
    return pm_chat_log


def DB_add_user_to_server(user_id, room_id):
    cursor = conn.cursor()
    SQL_ADD_USER_TO_SERVER = "INSERT INTO room_users (room_id, user_id) VALUES (%s, %s);"
    sql_values = (room_id, user_id)
    cursor.execute(SQL_ADD_USER_TO_SERVER, sql_values)
    conn.commit()
    cursor.close()

def DB_create_server(room_name, public_access, user_id):
    cursor = conn.cursor()
    CREATE_SERVER_SQL="CALL ADD_ROOM(%s, %s, %s);"
    sql_values = (room_name, public_access, user_id, )
    cursor.execute(CREATE_SERVER_SQL, sql_values)
    conn.commit()
    cursor.close()

@socketio.on('connect', namespace='/')
def connect():
    print('USER CONNECTED')
    socket_id = request.sid
    user_id = session['id']

    db_user_info = DB_get_user_info(user_id)
    language = db_user_info['language']
    print(db_user_info)
    username = session['user']
    last_room = db_user_info['last_room_id'] or 1

    # get users for room
    
    server_users = DB_get_server_users(last_room)
    # Get users server list
    server_list = DB_get_user_servers(user_id)

    # Create user object
    new_user = User(username=username, language=language, socket_id=socket_id, current_room=last_room)

    session['user_obj'] = new_user
    

    # Not in any servers add to general chat
    if len(server_list) == 0:
        rooms[1][username] =new_user
    # Add user to rooms they subscribe too 
    current_server_name= 'General Chat'
    for server in server_list:
        room_id = server['room_id'] 
        rooms[room_id][user_id] = new_user
        if server['room_id'] == last_room:
            current_server_name = server['room_name']
    
   
    print(dumps(server_users, indent=4))

    # DEBUG PRINTING
    print_user_details(user_id,username,socket_id,last_room)
    print_rooms()
    session['last_room'] =new_user.current_room
    emit('login', {'username' : username, 'numUsers':len(rooms),'language':language})

    chat_log = DB_get_chat_logs(last_room)

    print(server_users)
    for user in server_users:
        if int(user['user_id']) in rooms[last_room]:
            user['status'] = 'online'
        else:
            user['status'] = 'offline'

    emit('join server', {
        "server_id":last_room,
        "server_name": current_server_name,
        "chat_log":chat_log, 
        "server_users":server_users
        })
    emit('server info',{'server_list':server_list, "server_users":server_users})
    emit('user joined', {'user_id': user_id, 'username':username, 'numUsers':len(rooms)}, broadcast=True, include_self=False)
   
@socketio.on('query servers', namespace='/')
def query_server(search_term = None):
    socket_id = request.sid
    server_suggestions = DB_get_public_servers(search_term)

    emit('query servers', {"servers": server_suggestions} ,room=socket_id)



@socketio.on('create server', namespace='/')
def create_server(data):
    user_id = int(session['id'])
    room_name=data['room_name']
    public = data['public']
    DB_create_server(room_name, public, user_id)
   

@socketio.on('add server', namespace='/')
def query_server(server_info):
    user_id = int(session['id'])
    room_id = int(server_info['server_id'])
    DB_add_user_to_server(user_id, room_id)

    print('added user to room')



@socketio.on('join server', namespace='/')
def join_server(data):
    # get chat logs for server
    join_room = int(data['roomID'])
    print(join_room)
    user_id = session['id']

    username = data['username']
    session['last_room'] = join_room
    user_obj = session['user_obj']
    user_obj.current_room = join_room
    print(user_obj.__dict__)
    
    rooms[join_room][user_id] = user_obj
    print_rooms()
    # get chat logs (list of dictionaries) 
    room_chat_log = DB_get_chat_logs(join_room)
    # get users for room
    server_users = DB_get_server_users(join_room)
    

    for user in server_users:
            if int(user['user_id']) in rooms[join_room]:
                user['status'] = 'online'
            else:
                user['status'] = 'offline'
    emit('join server', {
        "server_id":join_room,
        "server_name":data['room'],
        "chat_log":room_chat_log, 
        "server_users":server_users
        })


@socketio.on('pm status', namespace='/')
def update_pm(data):
    
    my_user = session['id']
    user_obj = session['user_obj']
    other_user = data['active_pm_id']
    if other_user:
        user_obj.active_pm = int(other_user)
        pm_chat_log = DB_get_pm_chat_log(my_user, other_user)
        emit('pm log', pm_chat_log, room=request.sid)
    else:
        user_obj.active_pm = None

    


@socketio.on('private message',namespace='/')
def text(msg_data):
    print(msg_data)
    sender_id = int(session['id'])
    room_id = int(msg_data['room_id'])
    recipient_id = int(msg_data['recipient_id'])
    print(rooms[room_id][recipient_id])
    message=msg_data['message']
    sender_name = session.get('user')
    receiver = rooms[room_id][recipient_id]

    # only send if user has window open handle notification serverside
    # if receiver.active_pm == sender_id:
    #     emit('new private message', {
    #         'sender': sender_id,
    #         'message' : message
    #         }, include_self=False, room=receiver.socket_id)

    # Send and have client handle notification
    emit('new private message', {
            'sender_id': sender_id,
            'message' : message
            }, include_self=False, room=receiver.socket_id)

    DB_insert_private_msg(sender_id, recipient_id, message)
@socketio.on('new message',namespace='/')
def text(msg_data):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    message=msg_data['message']
    print(message)
    sender_name = session.get('user')
    user_id = int(session.get('id'))
    room_id = session['last_room']
    sender =rooms[room_id][user_id]

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
    user = session['user_obj']
    user.update_language_pref(language)

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




@socketio.on('start-transfer', namespace='/')
def start_transfer(filename, size):
    """Process an upload request from the client."""
    _, ext = os.path.splitext(filename)
    if ext in ['.exe', '.bin', '.js', '.sh', '.py', '.php']:
        return False  # reject the upload

    id = uuid.uuid4().hex  # server-side filename
    print(id)
    with open(current_app.config['FILEDIR'] + id + '.json', 'wt') as f:
        dump({'filename': filename, 'size': size}, f)
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

    
@socketio.on('upload', namespace='/')
def put_s3(file_data):
    filename = file_data['server_filename']
    file_title = file_data['file_title']
    room_id=session['last_room']
    sender_name = session.get('user')
    print(room_id)
    print('File ready', filename, file_title)
    fileloc= os.path.join(os.path.normpath(current_app.root_path), 'static/_files/')+filename
    upload_file(fileloc, 'anychatio', '{}/{}'.format(room_id, filename))
    file_url = '/'.join([current_app.config['CDN_URL'],str(room_id),filename])
    for username, receiver in rooms[room_id].items():
        if receiver.current_room == room_id:
            print(receiver.username)
            emit('file link', {'username': sender_name, 'file_url':file_url, 'filename': file_title}, room=receiver.socket_id)



@socketio.on('disconnect',namespace='/' )
def disconnect():
    """Sent by rooms when they leave a room.
    A status message is broadcast to all people in the room."""
    user_id = int(session['id'])

   
    
    last_room = session['user_obj'].current_room
    language = session['user_obj'].language
    cursor= conn.cursor()
    #update user info (last room) 
    sql_update_user_room = "UPDATE  users SET last_room_id = (%s), language = %s  where user_id = %s ;"
    sql_room_value = (last_room, language, user_id )
    cursor.execute(sql_update_user_room, sql_room_value)
    conn.commit()
    cursor.close()

    # delete user from cache
    for room, user_ids in rooms.items():
        if user_id in user_ids:
            del rooms[room][user_id]


    emit('user left', {'user_id':user_id, 'username':session['user'], 'numUsers':num_users}, broadcast=True)
    print('client disconnected')