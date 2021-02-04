import firebase_admin
from firebase_admin import firestore, credentials
from datetime import datetime
import time
import threading
import uuid

# ===================== setup =========================
# user name = u'karina'
cred = credentials.Certificate(r'C:\Users\asus\Downloads\Telegram Desktop\thresholdcryptochat-firebase-adminsdk-efq0t-9f4616190a.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
users = [u'karina', u'dmytro', u'pavlo']
shutdown = False
messages = []

def clear_collection(db):
    data = db.collection(u'messages')
    for d in data.stream():
        d.reference.delete()


def receving(user_name):

    while not shutdown:
        try:
            while True:
                read_ref = db.collection(u'messages')
                read_ref = read_ref.where(u'user', u'!=', user_name)
                for doc in read_ref.stream():
                    if doc.id not in messages:
                        messages.append(doc.id)
                        print(f"{doc.to_dict()[u'user']} => {doc.to_dict()[u'message'].decode('utf-8')}")
                time.sleep(10)
        except:
            pass


rT = threading.Thread(target=receving, args=(u'karina', ))
rT.start()

while shutdown == False:
    try:
        message = input().encode('utf-8')
        if message != "":
            doc_ref = db.collection(u'messages').document(str(uuid.uuid4()))
            doc_ref.set({u'message': message, u'user': u'karina'})
    except:
        shutdown = True

rT.join()