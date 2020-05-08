from googletrans import Translator
from time import time, sleep
from random import randint
from threading import Thread
from textblob import TextBlob, exceptions



LANG_SUPPORT = {
    "en" : "English",
    "zh-cn": "中文",
    "pl" : "Polski",
    "es" : "Español",
}
ran = randint(0,10)

start = time()
msg = f'One Sunday, at one of our weekly salsa sessions, my friend Frank brought along a Danish guest. I knew Frank spoke Danish well, because his mother was Danish, and he had lived in Denmark as a child. As for his friend, her English was fluent, as is standard for Scandinavians. However, to my surprise, during the evening’s chitchat it emerged that the two friends habitually exchanged emails using Google Translate. Frank would write a message in English, then run it through Google Translate to produce a new text in Danish; conversely, she would write a message in Danish, then let Google Translate anglicize it. How odd! Why would two intelligent people, each of whom spoke the other’s language well, do this? My own experiences with machine-translation software had always led me to be highly skeptical of it. But my skepticism was clearly not shared by these two. Indeed, many thoughtful people are quite enamored of translation programs, finding little to criticize in them. This baffles me.'

blob = TextBlob(msg)
for i in LANG_SUPPORT:
    starttrans = time()
    try:
        result = blob.translate(to=i)
    except exceptions.TextBlobError:
        result = msg
        pass
    endtrans= time()
    ela = endtrans-starttrans
    print(i, ':', result, f'time taken {ela:.2f}s')

print('\n\nGOOGLE')

t = Translator()

tran2 = []
# Multi
tran = []
threadpool= []
def getTrans(msg, dest):
    start = time()
    result = t.translate(msg, src='en', dest=dest).text
    tran.append(result)
    end = time()
    ela= end-start
    print(dest, ':', result, f'time taken {ela:.2f}s')

print('\nMulti')
for i in LANG_SUPPORT:
    transThread = Thread(target=getTrans, args=(msg,i))
    threadpool.append(transThread)
    transThread.start()

for thread in threadpool:
    thread.join()
# # Standard
# print('code continues')
# # for i in LANG_SUPPORT:
    
# #     result = t.translate(msg, src='en', dest=i).text
# #     tran2.append([i,result])

# print('translations',tran2)
end = time()

print('elapsed time:',f'{end-start}s')