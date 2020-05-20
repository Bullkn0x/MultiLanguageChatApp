from pymongo import MongoClient
from bson import ObjectId
import datetime

class dbHelper:
    def __init__(self):
        self.client = MongoClient("mongodb+srv://anychat:anychatadmin@cluster0-nbbi5.mongodb.net/?retryWrites=true&w=majority")
        self.db = self.client.anychatdb





def DB_add_message(message):
    messageID = messageCollection.insert_one(message).inserted_id
    print(messageID)

def DB_add_user(message):
    userID = userCollection.insert_one(message).inserted_id
    print(userID)

def DB_add_room(message):
    roomID = roomCollection.insert_one(message).inserted_id
    print(roomID)

def DB_replaceall_user(id, new):
    result = userCollection.replace_one(id,new)
    return result

#updates the user password
def DB_update_user_password(id, new):
    result = userCollection.update_one(id,{"$set": { 'password': new} })
    return result

def DB_replaceall_message(id, new):
    result = messageCollection.replace_one(id,new)
    return result

def DB_replaceall_room(id, new):
    result = roomCollection.replace_one(id,new)
    return result

#prints all the data inside a collection
def print_all_data(cursor):
    for data in cursor:
        print(data)
        print()

def getCurTime():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def DB_insert_msg(user, message, room_id, language):
    objectID = messageCollection.insert_one({'author':user,
     'message': message, 'room_id':room_id, 'channel_id':3, 'language':language}).inserted_id
    return objectID

#creates the room method
def DB_create_room(room_name, public_access, owner_id, user):
    roomID = roomCollection.insert_one({'room_name': room_name, 'public_access': public_access, 'owner_id': owner_id, 
    'create_time': getCurTime(), 'room_users':[user]}).inserted_id
    
    return roomID

def DB_insert_private_msg(sender, receiver, message):
    privMsgID = privateMessageCollection.insert_one({'sender': sender, 'receiver': receiver,
     'message':message, 'timestamp':getCurTime()}).inserted_id
    
    return privMsgID

#This function gets the dictionary of the owner after passing in the default roomID generated by MongoDB
def DB_get_owner_ID(room_id):
    print('\n\n')
    r = roomCollection.find({'_id':room_id})
    for data in r:
        for i in data['room_users']:
            if i['join_position']==1:
                return i
    
    return None

#function that returns the a user dictionary
def returnUser(userId, username, join_position):
    cT = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {'user_id':userId, 'user_name':username, 'join_position':join_position, 'join_date': cT, 'left_server': 0}

#return the dictionary of the user and insert into the database
def newUser(username, email, registered):
    newuser={'username':username, 'email':email, 'registered_on': registered}
    userCollection.insert_one(newuser)
    return newuser


#add a user to a room, user is a dictionary
def DB_add_user_to_room(room_id, user):
    roomCollection.update({'_id':room_id}, {'$push':{'room_users':user}})



def DB_get_user_info(user_id):
    r = userCollection.find({id:user_id})
    for i in r:
        print(i)


def DB_leave_server(user_id, room_id):

    return None


def DB_get_chat_logs(room_id):
    cursor = messageCollection.find({'room_id':room_id})
    data = ''
    for data in cursor:
        print(data)
    return data


#Get number of users in a room.
def DB_get_num_user_in_room(room_id):
    cursor = roomCollection.find({'_id': room_id})
    print("Number of users in the room is")
    for data in cursor:
        return len(data['room_users'])
    return None




anychatDB = dbHelper()

client = MongoClient("mongodb+srv://anychat:anychatadmin@cluster0-nbbi5.mongodb.net/?retryWrites=true&w=majority")
db = client.anychatdb
messageCollection = db.messages
userCollection = db.users
roomCollection = db.rooms
collectionList = db.list_collection_names()
privateMessageCollection = db.private_messages
print('collection list:')
print(collectionList)
if "private_messages" not in  collectionList:
    print('This IF statement is executed')
    # privateMessageCollection = db.createCollection('private_messages')
    privateMessageCollection = db['private_messages']
    privateMessageCollection.insert_one({'test':'test'})
    
collectionList = db.list_collection_names()
print('collection list AFTER:')
print(collectionList)
user = {'user_id': 2, 'user': 'faketsunami', 'email': 'new@new.com', 'language': 'pl'}

# cursor = userCollection.find()
# print_all_data(cursor)
# userCollection.insert_one(user)

result = DB_update_user_password({'_id': ObjectId('5eb532abff469c11c6397a1b')}, 'newtespass')

print(type(result))

# roomCollection.delete_one({'_id':ObjectId('5ebada07fdb4e29978cb2b3a')})



curTime = getCurTime()

#This line is initializing the variables to create a new room for testing purposes
# room_name = 'FFVII Remake'
# public_access = 1
# owner_id= 9
# firstUser = returnUser(10,'newtestuser',1)
# roomID = DB_create_room(room_name, public_access, owner_id, firstUser).inserted_id


#This is getting all the rooms and printing it out.
# roomCursor = roomCollection.find()
# print_all_data(roomCursor)
# print(collectionList)
# print('\n\n\nBEFORE UPDATE\n\n\n')
# print(DB_get_owner_ID(ObjectId('5ebb05b1b2868cb70bc219ce')))
# print('skip\n\n')
# cT = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# newUser = returnUser(11,'seconduser',2)
# DB_add_user_to_room(roomID,newUser)

# roomCursor = roomCollection.find()
# print_all_data(roomCursor)
# print('\n\n\n\nCHAT LOG')
# print(DB_get_chat_logs(25))


# print(DB_get_num_user_in_room(ObjectId('5ebb05b1b2868cb70bc219ce')))
# print(DB_insert_msg(user,'Test message',ObjectId('5ebb05b1b2868cb70bc219ce'),'en'))
# print('\nLINE ABOVE IS the INSERTED ID of the message\n')

# messageCursor = messageCollection.find().skip(messageCollection.count()-10)
# print_all_data(messageCursor)

print('\n\nSKIP')
sender = 1
receiver = 2
message = 'Can you receive the message'
DB_insert_private_msg(sender , receiver , message)
pmCursor = privateMessageCollection.find()
print_all_data(pmCursor)
print('\n\nSECOND SKIP')
privateMessageCollection.remove({'_id': ObjectId('5ec2edfc1663ea32249d9fd8')})
pmCursor = privateMessageCollection.find()
print_all_data(pmCursor)