#!/bin/python3

# This script subscribes another client (mobile phone) to our chat.

# Read
# https://firebase.google.com/docs/cloud-messaging/concept-options
#
# How to send messages:
# - explanation: https://firebase.google.com/docs/cloud-messaging/send-message#python_6
# - source code: https://github.com/firebase/firebase-admin-python/blob/b35abb9bb74ab7629ae1ff5c6f73772c6dd450c5/snippets/messaging/cloud_messaging.py#L24-L40
#
# https://firebase.google.com/docs/admin/setup/
# https://github.com/firebase/firebase-admin-python

# ================================================================================
# 1. read https://firebase.google.com/docs/admin/setup
# 2. sudo apt install python3-pip
# 3. sudo pip install firebase-admin

import firebase_admin

# This is registration token received on mobile phone from the client FCM SDKs.
# There is no way to receive it in Python: it is specific to the given app installation on the phone.
# Every chat client has such a token. All the communication is encrypted with this token.
# How it is received - see Android application at
# https://medium.com/@min2bhandari/firebase-cloud-messaging-with-kotlin-165ac1b0d841

# Replace this token with yours!
registration_token = "eT6B_xQRRFGVtK8xa71zBp:APA91bE9IK2wQtJkoLvEQdjhASPvmdFzxJs-sWedpbh3nSbUWinmtVZ10A8bun4YxG5UXaQHK3ExRZajQSYetdk-Yil-TEkKNjz03b_n45Yp5zV9ZHExtlIlbwr5dd5ukpNSQbx9RkuO"

# To make this initialization work you must have Firebase credentials in a file identified by environment variable in ~/.bashrc:
# export GOOGLE_APPLICATION_CREDENTIALS="/home/alex/Downloads/chat/threshold-chat-firebase-adminsdk-fg92b-3258681a34.json"
# Mentor will give this file. You must not commit it into GitHub!!!
firebase_admin.initialize_app()

# create Notification
notification = messaging.Message(android=messaging.AndroidConfig(ttl=datetime.timedelta(seconds=3600),priority='normal',notification=messaging.AndroidNotification(title='Try', body='It works!', icon='stock_ticker_update', color='#f45342')),topic="ThresholdChat")

# send (it must appear in Phone's tray as a pop-up notification)
response = messaging.send(notification)
