from pymongo import MongoClient
import  json

# client = MongoClient("mongodb+srv://anychat:anychatadmin@cluster0-nbbi5.mongodb.net/?retryWrites=true&w=majority")
# db = client.anychatdb


with open('messages.json') as f:
    messages = json.load(f)
    messages = messages["messages"]

with open('translations.json') as f:
    trans = json.load(f)
    trans = trans["translations"]


tempjson = {}
for i in trans:
    msgId = i['message_id']
    lang = i['language']
    msg = i['message']
    if msgId not in tempjson:
        tempjson[msgId] = {lang:msg}
    else:
        tempjson[msgId][lang] = msg

for i in messages:
    msgId = i['message_id']
    if msgId in tempjson:
        i['translations'] = tempjson[msgId]

with open('messagesUpdate.json', 'w') as f:

    json.dump(messages, f, indent=4, ensure_ascii=False)