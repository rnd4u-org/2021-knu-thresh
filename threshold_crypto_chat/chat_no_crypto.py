import firebase_admin
from firebase_admin import firestore, credentials
import threading
import uuid

# ===================== setup =========================
cred = credentials.Certificate(r'C:\Users\asus\Downloads\Telegram Desktop\thresholdcryptochat-firebase-adminsdk-efq0t-9f4616190a.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
user_name = u'karina'

def clear_collection(db):
    data = db.collection(u'messages')
    for d in data.stream():
        d.reference.delete()

clear_collection(db)
shutdown = False
messages = []

callback_done = threading.Event()
read_ref = db.collection(u'messages')

def on_snapshot(collection_snapshot, changes, read_time):
    for doc in collection_snapshot:
        if doc.id not in messages and doc.to_dict()[u'user'] != user_name:
            messages.append(doc.id)
            print(f"{doc.to_dict()[u'user']}=>{doc.to_dict()[u'message'].decode('utf-8')}")
    callback_done.set()


query_watch = read_ref.on_snapshot(on_snapshot)

while shutdown == False:
    try:
        message = input().encode('utf-8')
        if message != "":
            doc_ref = db.collection(u'messages').document(str(uuid.uuid4()))
            doc_ref.set({u'message': message, u'user': user_name})
    except:
        shutdown = True

