from pymongo import MongoClient
import  json



client = MongoClient("mongodb+srv://anychat:anychatadmin@cluster0-nbbi5.mongodb.net/?retryWrites=true&w=majority")
db = client.anychatdb
messageCollection = db.messages
message = {'user_id': 2, 'message': 'THIS IS AN ACTUAL TEST', 'timestamp': '2020-05-07 23:02:07.0', 'room_id': 25, 'deleted': 0, 'language': 'pl'}


messageID = messageCollection.insert_one(message).inserted_id

print(messageID)



