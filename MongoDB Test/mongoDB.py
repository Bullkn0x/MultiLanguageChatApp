from pymongo import MongoClient
from bson import ObjectId


class dbHelper:
    def __init__(self):
        self.client = MongoClient("mongodb+srv://anychat:anychatadmin@cluster0-nbbi5.mongodb.net/?retryWrites=true&w=majority")
        self.db = self.client.anychatdb






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
def DB_replaceall_user(old, new):
    result = userCollection.replace_one(old,new)
    return result

def DB_update_user(old, new):
    result = userCollection.update_one(old,new)
    return result

def DB_replaceall_message(old, new):
    result = messageCollection.replace_one(old,new)
    return result

def DB_replaceall_room(old, new):
    result = roomCollection.replace_one(old,new)
    return result

def print_all_data(cursor):
    for data in cursor:
        print(data)



anychatDB = dbHelper()

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
result = DB_update_user({'_id': ObjectId('5eb532abff469c11c6397a1b')}, {"$set": { 'email': 'idk@whoknowns.com'}})
print(result)
cursor = userCollection.find()
print_all_data(cursor)
