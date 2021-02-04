import firebase_admin
from firebase_admin import firestore, credentials
from datetime import datetime
import time
import threading
import uuid
# ===================== setup =========================
# user name = u'dimas'
cred = credentials.Certificate(r'C:\Users\User\Desktop\thresholdcryptochat-firebase-adminsdk-efq0t-9f4616190a.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
users = [u'karina', u'dmytro', u'pavlo']

def clear_collection(db):
    data = db.collection(u'messages')
    for d in data.stream():
        d.reference.delete()

shutdown = False
messages = []

def receving(user_name):

    while not shutdown:
        read_ref = db.collection(u'messages')
        read_ref = read_ref.where(u'user', u'!=', u'dimas')
        for doc in read_ref.stream():
            if doc.id not in messages:
                messages.append(doc.id)
                print(f"{doc.to_dict()[u'user']} => {doc.to_dict()[u'message'].decode('utf-8')}")
        time.sleep(10)




rT = threading.Thread(target=receving, args=(u'dimas', ))
rT.start()

while shutdown == False:
    try:
        message = input().encode('utf-8')
        if message != "":
            doc_ref = db.collection(u'messages').document(str(uuid.uuid4()))
            doc_ref.set({u'message': message, u'user': u'dimas'})

        #time.sleep(2)
    except:
        shutdown = True

rT.join()
