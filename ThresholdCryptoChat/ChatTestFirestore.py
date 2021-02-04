import firebase_admin
from firebase_admin import firestore, credentials
from datetime import datetime
import time
import threading
import uuid

# ===================== setup =========================
# user name = u'karina'
cred = credentials.Certificate(r'C:\GAMES\SecretFolder\thresholdcryptochat-firebase-adminsdk-efq0t-9f4616190a.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
users = [u'karina', u'dmytro', u'pavlo']
#p = 21236934862218511653623447364710811485097463859632312183494470321865437684383737237095118043782630953663551424644349676344051737646575908035229445418970350579998208464171222735264502195941087943912660267879360376600529021906143975135547131090543473264136217654462045160443124694552287906754023396731536363634457064852718052465363129643486360313019964341460374106944280350493228300541853254188973394324275526119409082151906335458925803081691961627262872909544911250939426559669641181741418792650389621395244191383680090126152455331128151622579879305128105513594663146479955290034772381144185556023460209436347971723223

def clear_collection(db):
    data = db.collection(u'messages')
    for d in data.stream():
        d.reference.delete()

clear_collection(db)
shutdown = False
messages = []

def receving(user_name):

    while not shutdown:
        read_ref = db.collection(u'messages')
        read_ref = read_ref.where(u'user', u'!=', u'pashka-cheburashka')
        for doc in read_ref.stream():
            if doc.id not in messages:
                messages.append(doc.id)
                print(f"{doc.to_dict()[u'user']} => {doc.to_dict()[u'message'].decode('utf-8')}")
        time.sleep(5)




rT = threading.Thread(target=receving, args=(u'pashka-cheburashka', ))
rT.start()

while shutdown == False:
    try:
        message = input().encode('utf-8')
        if message != "":
            doc_ref = db.collection(u'messages').document(str(uuid.uuid4()))
            doc_ref.set({u'message': message, u'user': u'pashka-cheburashka'})

        #time.sleep(2)
    except:
        shutdown = True

rT.join()

# #!/bin/python3
#
# # This script gives a short example of Cloud Firestore - based chat.
# # Read:
# # - Cloud Firebase Python manual at https://firebase.google.com/docs/firestore/quickstart#python
# # - chat Android app (to take chat structure): https://www.ericdecanini.com/2019/12/16/instant-chat-messenger-with-cloud-firestore
#
# # ================================================================================
# # 1. read https://firebase.google.com/docs/admin/setup
# # 2. sudo apt install python3-pip
# # 3. sudo pip3 install firebase-admin
#
# import firebase_admin
# from firebase_admin import firestore
# from datetime import datetime
# import uuid
#
# # ===================== setup Firebase credentials =========================
#
# # update this with you Firebase credentials
# from firebase_admin import credentials
# # cred = credentials.Certificate('/home/alex/Downloads/chat/threshold-chat-firebase-adminsdk-fg92b-3258681a34.json')
# cred = credentials.Certificate('C:\GAMES\SecretFolder\\votechatcrypto-firebase-adminsdk-qr0f2-6de712738a.json')
# # default initialization based on
# # export GOOGLE_APPLICATION_CREDENTIALS="/home/alex/Downloads/chat/threshold-chat-firebase-adminsdk-fg92b-3258681a34.json"
# # Mentor will give this file. You must not commit it into GitHub!!!
# # firebase_admin.initialize_app()
#
# # initialization with explicitly indicated credentials
# firebase_admin.initialize_app(cred)
#
# # for several chats on one PC:
# # cred = credentials.ApplicationDefault()
# # firebase_admin.initialize_app(cred, {'projectId': project_id,})
#
# db = firestore.client()
#
# # ===================== send message ==========================
# doc_ref = db.collection(u'users').document(u'UserGUID').collection(u'rooms').document(u'RoomID').collection(u'messages').document(str(uuid.uuid4()))
# doc_ref.set({u'text': u'message 3 pashenьka', u'user': u'pavlo', u'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")})
#
# #
# # # ===================== read messages =========================
# read_ref = db.collection(u'users').document(u'UserGUID').collection(u'rooms').document(u'RoomID').collection(u'messages')
# for doc in read_ref.stream():
#     print(f'{doc.id} => {doc.to_dict()}')