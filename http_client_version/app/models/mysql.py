from .. import mysql

class dbHelper:

    def __init__(self):
        self.conn= mysql.connect()
        self.cursor = self.conn.cursor()

    def queryAll(self,sql, params=None):
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    def queryOne(self,sql, params=None):
        self.cursor.execute(sql, params)
        return self.cursor.fetchone()

    def insert(self,sql, params=None):
        self.cursor.execute(sql, params)
        self.conn.commit()

    def insertMany(self,sql, params=None):
        self.cursor.executemany(sql, params)
        self.conn.commit()

    def insertReturn(self,sql, params=None):
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor.fetchone()

    def delete(self,sql, params=None):
        self.cursor.execute(sql, params)
        self.conn.commit()
    
    def deleteReturn(self,sql, params=None):
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor.fetchone()

    def update(self,sql, params=None):
        self.cursor.execute(sql, params)
        self.conn.commit()
    
    def updateReturn(self,sql, params=None):
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor.fetchone()
    
         
anyChatDB = dbHelper()


def DB_chat_log_by_lang(lang_code, room_id):
    SQL_CHAT_BY_LANG='CALL CHAT_LOG_BY_LANG(%s , %s);'
    sql_params = (lang_code, room_id, )
    logs = anyChatDB.queryAll(SQL_CHAT_BY_LANG,sql_params)
    return logs

def DB_add_translations(message_id, message_tuples):


    SQL_BULK_ADD = f"""INSERT INTO translations (message_id, `language`, message) 
                        VALUES({message_id}, %s, %s);"""

    anyChatDB.insertMany(SQL_BULK_ADD, message_tuples)

def DB_populate_cache():

    SQL_GET_ROOMS = "SELECT room_id from rooms;"
    all_rooms = anyChatDB.queryAll(SQL_GET_ROOMS)
    
    return all_rooms

def DB_get_chat_logs(room_id):

    SQL_ROOM_CHAT = "CALL ROOM_CHAT_LOG(%s)"
    sql_where = (room_id, )
    room_chat_log = anyChatDB.queryAll(SQL_ROOM_CHAT, sql_where)

    return room_chat_log

def DB_get_user_info(user_id):

    SQL_GET_USER = "SELECT * FROM users WHERE user_id = %s;"
    sql_where = (user_id, )    
    user_info = anyChatDB.queryOne(SQL_GET_USER, sql_where)
    
    return user_info

def DB_insert_msg(user_id, message, room_id, language):
    
    SQL_INSERT_MSG = 'CALL ADD_MESSAGE(%s, %s, %s , %s);'
    sql_params = (user_id, message, room_id, language, )
    message_id = anyChatDB.insertReturn(SQL_INSERT_MSG,sql_params)
    print(message_id)

    return message_id['message_id']
    

def DB_get_user_servers(user_id):
    SQL_USER_SERVERS = "CALL USER_SERVERS(%s);"
    sql_params = (user_id, )
    server_list = anyChatDB.queryAll(SQL_USER_SERVERS, sql_params)

    return server_list


def DB_get_server_userlist(room_id):
    SQL_SERVER_USERLIST = "CALL SERVER_USERLIST(%s);"
    sql_where = (room_id, )
    server_users = anyChatDB.queryAll(SQL_SERVER_USERLIST,sql_where)

    return server_users

def DB_get_public_servers(user_id, search_term=None):

    SQL_GET_PUBLIC_SERVERS = "CALL PUBLIC_SERVERLIST(%s, %s);"
    sql_params = (search_term, int(user_id), )
    public_servers = anyChatDB.queryAll(SQL_GET_PUBLIC_SERVERS, sql_params)

    return public_servers



def DB_insert_private_msg(from_user, to_user, message):

    SQL_INSERT_PM = 'CALL ADD_PRIVATE_MESSAGE(%s,%s,%s);'
    sql_params = (from_user, to_user, message, )
    message_id = anyChatDB.insertReturn(SQL_INSERT_PM,sql_params)
    

    return message_id

def DB_get_pm_chat_log(me, them):

    SQL_GET_PM_LOG = "CALL PM_CHAT_LOG(%s, %s);"
    sql_params = (me, them,)
    pm_chat_log = anyChatDB.queryAll(SQL_GET_PM_LOG, sql_params)
    return pm_chat_log


def DB_change_pw(pw, user_id):
    SQL_UPDATE_USER_PASSWORD ='UPDATE users SET password=%s WHERE user_id=%s;'
    print("The PW is")
    print(pw)
    sql_values = (pw, user_id)
    anyChatDB.update(SQL_UPDATE_USER_PASSWORD, sql_values)
    


def DB_add_user_to_server(user_id, room_id):

    SQL_ADD_USER_TO_SERVER = "CALL JOIN_ROOM(%s, %s);"
    sql_values = (room_id, user_id)
    room_details = anyChatDB.insertReturn(SQL_ADD_USER_TO_SERVER,sql_values)
    return room_details

def DB_create_server(room_name, public_access, user_id):

    CREATE_SERVER_SQL="CALL ADD_ROOM(%s, %s, %s);"
    sql_params = (room_name, public_access, user_id, )
    room_details = anyChatDB.insertReturn(CREATE_SERVER_SQL,sql_params)

    return room_details

def DB_delete_msg(message_id):
    
    SQL_DELETE_MESSAGE = "CALL DELETE_MESSAGE(%s);"
    sql_params = (message_id, )
    anyChatDB.delete(SQL_DELETE_MESSAGE,sql_params)

#Method to delete the row where the user is in the room.
def DB_leave_server(user_id, room_id):
    LEAVE_SERVER_SQL ='CALL LEAVE_SERVER(%s ,%s);'
    sql_params = (user_id,room_id )
    print('bieeeee')
    anyChatDB.delete(LEAVE_SERVER_SQL,sql_params)

def DB_server_update_color(color, room_id):
    SQL_UPDATE_SERVER_COLOR ='UPDATE rooms SET color=%s WHERE room_id=%s;'
    sql_values = (color,room_id, )
    anyChatDB.update(SQL_UPDATE_SERVER_COLOR, sql_values)


def DB_user_disconnect(last_room,language, user_id):
    SQL_UPDATE_USER = "UPDATE users SET last_room_id = (%s), language = %s  where user_id = %s ;"
    sql_params = (last_room,language, user_id, )
    anyChatDB.update(SQL_UPDATE_USER, sql_params)
