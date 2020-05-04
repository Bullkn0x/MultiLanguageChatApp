from flask import session, request,Response, redirect, current_app
from flask_socketio import emit, join_room, leave_room, rooms
from .. import socketio
from werkzeug.security import generate_password_hash as hash_pass, check_password_hash as check_pass
from .utils import try_translate, print_rooms, print_user_details, LANG_SUPPORT, translateMany
from .awsHelper import upload_file
from ..models.user import User
from ..models.mysql import *
from json import dumps, dump
import uuid
import os
from threading import Thread, current_thread, RLock
import multiprocessing as mp



# populate room info
rooms_resp = DB_populate_cache()
print(rooms_resp)
# create dictionary of rooms to track online users
rooms = {row['room_id']: {} for row in rooms_resp}
print(rooms)
num_users=0


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
    
    server_users = DB_get_server_userlist(last_room)
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



    # DEBUG PRINTING
    print_user_details(user_id,username,socket_id,last_room)
    print_rooms(rooms)
    session['last_room'] =new_user.current_room
    emit('login', {'username' : username, 'numUsers':len(rooms),'language':language})

    # without translate
    # chat_log = DB_get_chat_logs(last_room)
    # By language
    print(language)
    chat_log = DB_chat_log_by_lang(language, last_room)
    print(chat_log)
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
    user_id = int(session['id'])
    print(search_term, user_id)
    socket_id = request.sid
    server_suggestions = DB_get_public_servers(user_id, search_term)

    emit('query servers', {"servers": server_suggestions} ,room=socket_id)

#Method to Add a server to the User Server List
@socketio.on('add server', namespace='/')
def add_server(server_info):
    user_id = int(session['id'])
    room_id = int(server_info['server_id'])
    
    room_info = DB_add_user_to_server(user_id, room_id)
    print(room_info)
    emit('new server', room_info)
    print('added user to room')


@socketio.on('create server', namespace='/')
def create_server(data):
    user_id = int(session['id'])
    user_obj = session['user_obj']
    room_name=data['room_name']
    public = data['public']
    room_info = DB_create_server(room_name, public, user_id)
    room_id = room_info['room_id']
    # Add room and user to room monitoring cache
    rooms[room_id] = {user_id : user_obj}
    print_rooms(rooms)
    print('server created', room_info)
    emit('new server', room_info)


# @socketio.on('more chat', namespace='/')
# def get_next_50(data):


@socketio.on('join server', namespace='/')
def join_server(data):
    # get chat logs for server
    user_obj = session['user_obj']
    join_room = int(data['roomID'])
    

    print(join_room)
    user_id = session['id']

    username = user_obj.username
    session['last_room'] = join_room
    user_obj.current_room = join_room
    
    rooms[join_room][user_id] = user_obj
    print_rooms(rooms)

    language = user_obj.language
    # without translate
    # room_chat_log = DB_get_chat_logs(last_room)
    # By language
    room_chat_log = DB_chat_log_by_lang(language, join_room)

    # get users for room
    server_users = DB_get_server_userlist(join_room)
    
    #get the owner id
    owner_id = DB_get_owner_id(join_room)
    

    print('THE ROOM OWNER ID IS: ')
    print(owner_id)

    print('The USER ID is: ')
    print(user_id)


    if owner_id['owner_id'] == user_id:
        emit('delete button', {
            "owner_id": owner_id,
            "server_name": data['room']
        })
        #show the menu for delete the room here
        print('show the menu for delete the room')
    else:
        emit('hide button', {
            "owner_id": owner_id,
            "server_name": data['room']
        })
        print('hide the menu for the delete room')

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


@socketio.on('change password', namespace='/')
def change_password(data):
    user_id = session['id']
    oldPassword = str(data['oldPassword'])
    newPassword = str(data['newPassword'])
    db_user = DB_get_user_info(user_id)
    print('THE DB USER IS:')
    print(db_user)
    if db_user and check_pass(db_user['password'], oldPassword):
        print('NEW PASSWORD2' , newPassword)
        print('OLD PASSWORD2' , oldPassword)
        DB_change_pw(hash_pass(newPassword,method='sha256'),user_id)
        emit('password confirmation', 'Password Successfully Changed!')
    else:
        emit('password confirmation', 'Your Password is Invalid!')
    

@socketio.on('private message',namespace='/')
def private_text(msg_data):
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
    sender = session['user_obj']
    sender_name = session.get('user')
    sender_language = sender.language
    room_id = sender.current_room
    message = msg_data['message']
    temp_msg_id = msg_data['temp_msg_id']
    user_id = int(session.get('id'))
    room_id = session['last_room']
    # get actual message id from db and insert record
    message_id = DB_insert_msg(user_id, message, room_id, sender_language)
    translations = getTranslations(message, sender_language)
    # Iterate through rooms users and emit message to usersocket 
    for username, receiver in rooms[room_id].items():
        if receiver.current_room == room_id:
            # and receiver.language!='original'
            message_out = translations[receiver.language]
            # it using js on enter key, ignore them for now
            emit('new message', {
                'username': sender_name, 
                "message":message_out,
                "message_id" :message_id,
                "room_id": room_id,
                "temp_msg_id":temp_msg_id}, include_self=True, room=receiver.socket_id)
        
        print('sent')

    DB_add_translations(message_id, translations.items())
    

    print('CACHE DETAILS', try_translate.cache_info())
    
def getTranslations(msg, sender_language):
    processes = []
    translations = mp.Manager().dict()
    for to_lang in LANG_SUPPORT:
        p = mp.Process(target=translateMany, args=(msg, sender_language, to_lang, translations))
        p.start()
        processes.append(p)
    for process in processes:
        process.join()

    return translations

@socketio.on('message update')
def handle_message_operation(data):
    room_id = session['last_room']
    if data['operation'] == 'edit':
        pass
    if data['operation'] == 'delete':
        print(data)
        DB_delete_msg(data['message_id'])
        for username, receiver in rooms[room_id].items():
            if receiver.current_room == room_id:
                emit('message update', { 
                    'operation':data['operation'],
                    'message_id': data['message_id'] 
                    }, room=receiver.socket_id)

    if data['operation'] == 'pin':
        pass

@socketio.on('server update')
def handle_server_operation(data):
    room_id = data['room_id']
    color = data['color']
    if data['operation'] == 'update_color':
        print(data)
        DB_server_update_color(color,room_id)
    
        emit('server update', { 
            'operation':data['operation'],
            'room_id': data['room_id'],
            'color': color
            }, broadcast=True)

        
@socketio.on('user update')
def handle_user_operation(data):
    user_id = int(session['id'])
    if data['operation'] =='leave_server':
        DB_leave_server(user_id, data['room_id'])
    
        print('user left the server')


@socketio.on('change language',namespace='/')
def update_language(data):
    user = session['user_obj']
    user.update_language_pref(data['language'])
    room_id = user.current_room
    chat_log = DB_chat_log_by_lang(data['language'], room_id)

    emit('chat refresh', {"server_name":data['room_name'],"server_id": room_id,"chat_log":chat_log })


@socketio.on('typing',namespace='/')
def user_typing():
    room_id = session['last_room']
    for username, receiver in rooms[room_id].items():
        if receiver.current_room == room_id:
            emit('typing', { 'username':session['user'] }, include_self=False, room=receiver.socket_id)

@socketio.on('stop typing',namespace='/')
def user_stopped_typing():
    room_id = session['last_room']
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

    #update user info (last room) 
    DB_user_disconnect(last_room, language, user_id)

    # delete user from cache
    for room, user_ids in rooms.items():
        if user_id in user_ids:
            del rooms[room][user_id]


    emit('user left', {'user_id':user_id, 'username':session['user'], 'numUsers':num_users}, broadcast=True)
    print('client disconnected')