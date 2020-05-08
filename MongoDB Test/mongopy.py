from pymongo import MongoClient
import  json



client = MongoClient("mongodb+srv://anychat:anychatadmin@cluster0-nbbi5.mongodb.net/?retryWrites=true&w=majority")
db = client.anychatdb
messageCollection = db.messages
print(messageCollection)

with open('messagesUpdate.json') as f:
    messages = json.load(f)

for i in messages:
    messageCollection.insert_one(i)
