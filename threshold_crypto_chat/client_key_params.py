import firebase_admin
from firebase_admin import firestore, credentials
import json

cred = credentials.Certificate(r'C:\Users\asus\Downloads\Telegram Desktop\thresholdcryptochat-firebase-adminsdk-efq0t-9f4616190a.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

user_name = u'karina'

read_ref = db.collection(u'key_params')
read_ref = read_ref.where(u'user', u'==', user_name)
for doc in read_ref.stream():
    key_parameters = doc.to_dict()

with open('key_parameters.json', 'w') as json_file:
    json.dump(key_parameters, json_file)
