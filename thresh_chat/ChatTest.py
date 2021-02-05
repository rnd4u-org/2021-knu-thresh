
import firebase_admin
from firebase_admin import firestore, credentials
from datetime import datetime
import time
import threading
import uuid

# ===================== setup =========================
# user name = u'karina'
cred = credentials.Certificate(r'C:\Users\User\Desktop\thresholdcryptochat-firebase-adminsdk-efq0t-9f4616190a.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
users = [u'karina', u'dmytro', u'pavlo']

def clear_collection(db):
    data = db.collection(u'messages')
    for d in data.stream():
        d.reference.delete()

clear_collection(db)
shutdown = False
messages = []


read_ref = db.collection(u'messages')
callback_done = threading.Event()
def on_snapshot(collection_snapshot, changes, read_time):
    for doc in collection_snapshot:
        if doc.id not in messages and doc.to_dict()[u'user'] != 'dimas':
            messages.append(doc.id)
            print(u"{}=>{}".format(doc.to_dict()[u'user'], doc.to_dict()[u'message'].decode("utf-8")))
    callback_done.set()

query_watch = read_ref.on_snapshot(on_snapshot)
# rT = threading.Thread(target=receving, args=(u'pashka-cheburashka', ))
# rT.start()aa


while shutdown == False:
    try:
        message = input().encode('utf-8')
        if message != "":
            doc_ref = db.collection(u'messages').document(str(uuid.uuid4()))
            doc_ref.set({u'message': message, u'user': u'dimas'})

        #time.sleep(2)
    except:
        shutdown = True
