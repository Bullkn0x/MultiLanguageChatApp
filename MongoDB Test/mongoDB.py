from pymongo import MongoClient
from bson import ObjectId


class dbHelper:
    def __init__(self):
        self.client = MongoClient("mongodb+srv://anychat:anychatadmin@cluster0-nbbi5.mongodb.net/?retryWrites=true&w=majority")
        self.db = self.client.anychatdb


anychatDB = dbHelper()



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
def DB_replaceall_user(id, new):
    result = userCollection.replace_one(id,new)
    return result

def DB_update_user_password(id, new):
    result = userCollection.update_one(id,{"$set": { 'password': new} })
    return result

def DB_replaceall_message(id, new):
    result = messageCollection.replace_one(id,new)
    return result

def DB_replaceall_room(id, new):
    result = roomCollection.replace_one(id,new)
    return result

def print_all_data(cursor):
    for data in cursor:
        print(data)

def DB_insert_msg(user_id, message, room_id, language):
    objectID = userCollection.insert_one({'user_id':user_id, 'message': message, 'room_id':room_id, 'language':language}).inserted_id
    return objectID

def DB_add_user_to_server(user_id, room_id):
    roomCollection.insert_one({},{})

def DB_get_user_info(user_id):
    r = userCollection.find({id:user_id})
    for i in r:
        print(i)



client = MongoClient("mongodb+srv://anychat:anychatadmin@cluster0-nbbi5.mongodb.net/?retryWrites=true&w=majority")
db = client.anychatdb
messageCollection = db.messages
userCollection = db.users
roomCollection = db.rooms

user = {'user_id': 2, 'user': 'faketsunami', 'email': 'new@new.com', 'language': 'pl'}

cursor = userCollection.find()
print_all_data(cursor)
print('\n\n\nBEFORE UPDATE\n\n\n')
# userCollection.insert_one(user)

result = DB_update_user_password({'_id': ObjectId('5eb532abff469c11c6397a1b')}, 'newtespass')

print(type(result))
# cursor = userCollection.find()
# print_all_data(cursor)
