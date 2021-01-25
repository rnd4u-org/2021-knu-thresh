#!/bin/python3

# This script gives a short example of Cloud Firestore - based chat.
# Read:
# - Cloud Firebase Python manual at https://firebase.google.com/docs/firestore/quickstart#python
# - chat Android app (to take chat structure): https://www.ericdecanini.com/2019/12/16/instant-chat-messenger-with-cloud-firestore

# ================================================================================
# 1. read https://firebase.google.com/docs/admin/setup
# 2. sudo apt install python3-pip
# 3. sudo pip3 install firebase-admin

import firebase_admin
from firebase_admin import firestore
from datetime import datetime
import uuid

# ===================== setup Firebase credentials =========================

# update this with you Firebase credentials
from firebase_admin import credentials
cred = credentials.Certificate('/home/alex/Downloads/chat/threshold-chat-firebase-adminsdk-fg92b-3258681a34.json')

# default initialization based on 
# export GOOGLE_APPLICATION_CREDENTIALS="/home/alex/Downloads/chat/threshold-chat-firebase-adminsdk-fg92b-3258681a34.json"
# Mentor will give this file. You must not commit it into GitHub!!!
# firebase_admin.initialize_app()

# initialization with explicitly indicated credentials
firebase_admin.initialize_app(cred) 

# for several chats on one PC:
# cred = credentials.ApplicationDefault()
# firebase_admin.initialize_app(cred, {'projectId': project_id,})

db = firestore.client()

# ===================== send message ==========================
doc_ref = db.collection(u'users').document(u'UserGUID').collection(u'rooms').document(u'RoomID').collection(u'messages').document(str(uuid.uuid4()))
doc_ref.set({u'text': u'rrrrrrr', u'user': u'uuuuuuu', u'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")})

# ===================== read messages =========================
read_ref = db.collection(u'users').document(u'UserGUID').collection(u'rooms').document(u'RoomID').collection(u'messages')
for doc in read_ref.stream():
    print(f'{doc.id} => {doc.to_dict()}')
    
    
    
    
