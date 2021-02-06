import firebase_admin
from firebase_admin import firestore, credentials
import json

cred = credentials.Certificate(r'C:\Users\asus\Downloads\Telegram Desktop\votechatcrypto-firebase-adminsdk-qr0f2-6de712738a.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

user_name = u'karina'

# Read crypto parameters from firestore db
read_ref = db.collection(u'key_params')
read_ref = read_ref.where(u'user', u'==', user_name)
for doc in read_ref.stream():
    key_parameters = doc.to_dict()

# Save crypto parameters to 'key_parameters.json' file
with open('key_parameters.json', 'w') as json_file:
    json.dump(key_parameters, json_file)
