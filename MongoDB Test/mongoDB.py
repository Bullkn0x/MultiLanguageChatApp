from pymongo import MongoClient



class dbHelper:
    def __init__(self):
        self.client = MongoClient("mongodb+srv://anychat:anychatadmin@cluster0-nbbi5.mongodb.net/?retryWrites=true&w=majority")
        self.db = self.client.anychatdb



anychatDB = dbHelper()

client = MongoClient("mongodb+srv://anychat:anychatadmin@cluster0-nbbi5.mongodb.net/?retryWrites=true&w=majority")
db = client.anychatdb

messageCollection = db.messages
userCollection = db.users
roomCollection = db.rooms


# messageCollection.insert_one(message)

def DB_add_message(message):
    messageID = messageCollection.insert_one(message).inserted_id
    print(messageID)

def DB_add_user(message):
    userID = userCollection.insert_one(message).inserted_id
    print(userID)

def DB_add_room(message):
    roomID = roomCollection.insert_one(message).inserted_id
    print(roomID)

#this method updates, update user is deprecated
def DB_update_user(old, new):
    result = userCollection.replace_one(old,new)
    return result

def DB_update_message(old, new):
    result = messageCollection.replace_one(old,new)
    return result

def DB_update_room(old, new):
    result = roomCollection.replace_one(old,new)
    return result


        



message = {'user_id': 2, 'message': 'THIS IS AN ACTUAL TEST', 'timestamp': '2020-05-07 23:02:07.0', 'room_id': 25, 'deleted': 0, 'language': 'pl'}
