import firebase_admin
from firebase_admin import firestore, credentials
from threshold_crypto import ThresholdCrypto, ThresholdParameters, KeyParameters, PublicKey, KeyShare, EncryptedMessage
import time
import threading
import uuid

# ===================== setup =========================
# user name = u'karina'
cred = credentials.Certificate(r'C:\GAMES\SecretFolder\thresholdcryptochat-firebase-adminsdk-efq0t-9f4616190a.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
users = [u'karina', u'dmytro', u'pavlo']
user_name = u'pavlo'
shutdown = False
messages = []

def clear_collection(db, collection):
    data = db.collection(collection)
    for d in data.stream():
        d.reference.delete()

clear_collection(db, u'crypto_message')

def create_crypto_params_int():
    # Generate parameters, public key and shares
    key_params = ThresholdCrypto.static_2048_key_parameters()
    thresh_params = ThresholdParameters(2, 3)
    pub_key, key_shares = ThresholdCrypto.create_public_key_and_shares_centralized(key_params, thresh_params)
    p = key_params.p
    q = key_params.q
    g = key_params.g
    n = 3
    t = 2
    pub_key = pub_key.g_a
    share1 = [key_shares[0].x, key_shares[0].y]
    share2 = [key_shares[1].x, key_shares[1].y]
    share3 = [key_shares[2].x, key_shares[2].y]
    return p, q, g, n, t, pub_key, share1, share2, share3


def create_crypto_params_str(p, q, g, n, t, pub_key, share1, share2, share3):
    p = str(p)
    q = str(q)
    g = str(g)
    pub_key = str(pub_key.g_a)
    share1 = [share1[0], str(share1[1])]
    share2 = [share2[0], str(share2[1])]
    share3 = [share3[0], str(share3[1])]
    return p, q, g, n, t, pub_key, share1, share2, share3


def regenerate_crypto_params_objects(p, q, g, n, t, pub_key, share1, share2, share3):
    key_params = KeyParameters(p, q, g)
    thresh_params = ThresholdParameters(t, n)
    pub_key = PublicKey(pub_key, key_params)
    shares = []
    share1 = KeyShare(share1[0], share1[1], key_params)
    share2 = KeyShare(share2[0], share2[1], key_params)
    share3 = KeyShare(share3[0], share3[1], key_params)
    shares.append(share1)
    shares.append(share2)
    shares.append(share3)
    return key_params, thresh_params, pub_key, shares


def prepare_values_str_to_int(values):
    p = int(values[u'p'])
    q = int(values[u'q'])
    g = int(values[u'g'])
    n = values[u'n']
    t = values[u't']
    pub_key = int(values[u'pub_key'])
    share1 = [values[u'share1'][0], int(values[u'share1'][1])]
    share2 = [values[u'share2'][0], int(values[u'share2'][1])]
    share3 = [values[u'share3'][0], int(values[u'share3'][1])]
    return p, q, g, n, t, pub_key, share1, share2, share3


def receiving(user_name):

    while not shutdown:
        while True:
            read_ref = db.collection(u'crypto_message')
            read_ref = read_ref.where(u'user', u'!=', user_name)
            for doc in read_ref.stream():
                if doc.id not in messages:
                    messages.append(doc.id)

                    values = doc.to_dict()
                    encrypted_message = values[u'message']
                    v = int(values[u'v'])
                    c = int(values[u'c'])

                    encrypted_message = EncryptedMessage(v, c, encrypted_message)

                    p, q, g, n, t, pub_key, share1, share2, share3 = prepare_values_str_to_int(values)
                    key_params, thresh_params, pub_key, shares = regenerate_crypto_params_objects(p, q, g, n, t,
                                                                                                  pub_key, share1,
                                                                                                  share2, share3)

                    # build partial decryptions of three share owners using their shares
                    reconstruct_shares = [shares[i] for i in [0, 2]]
                    partial_decryptions = [ThresholdCrypto.compute_partial_decryption(encrypted_message, share)
                                           for share in reconstruct_shares]

                    # combine these partial decryptions to recover the message
                    decrypted_message = ThresholdCrypto.decrypt_message(partial_decryptions, encrypted_message,
                                                                        thresh_params, key_params)

                    print(f"{doc.to_dict()[u'user']} => {decrypted_message}")
            time.sleep(4)


receivingThread = threading.Thread(target=receiving, args=(user_name,))
receivingThread.start()

while shutdown == False:

    message = input()
    if message != "":
        p, q, g, n, t, pub_key, share1, share2, share3 = create_crypto_params_int()
        key_params, thresh_params, pub_key, shares = regenerate_crypto_params_objects(p, q, g, n, t, pub_key, share1,
                                                                                      share2, share3)
        encrypted = ThresholdCrypto.encrypt_message(message, pub_key)
        encrypted_message = encrypted.enc
        v = str(encrypted.v)
        c = str(encrypted.c)

        p, q, g, n, t, pub_key, share1, share2, share3 = create_crypto_params_str(p, q, g, n, t, pub_key, share1,
                                                                                  share2, share3)

        doc_ref = db.collection(u'crypto_message').document(str(uuid.uuid4()))
        doc_ref.set({u'user': user_name, u'p': p, u'q': q, u'g': g, u'n': n, u't': t, u'pub_key': pub_key,
                     u'share1': share1, u'share2': share2, u'share3': share3, u'message': encrypted_message, u'v': v, u'c': c})


receivingThread.join()

# import firebase_admin
# from firebase_admin import firestore, credentials
# from datetime import datetime
# import time
# import threading
# import uuid
#
# # ===================== setup =========================
# # user name = u'karina'
# cred = credentials.Certificate(r'C:\GAMES\SecretFolder\thresholdcryptochat-firebase-adminsdk-efq0t-9f4616190a.json')
# firebase_admin.initialize_app(cred)
# db = firestore.client()
# users = [u'karina', u'dmytro', u'pavlo']
# #p = 21236934862218511653623447364710811485097463859632312183494470321865437684383737237095118043782630953663551424644349676344051737646575908035229445418970350579998208464171222735264502195941087943912660267879360376600529021906143975135547131090543473264136217654462045160443124694552287906754023396731536363634457064852718052465363129643486360313019964341460374106944280350493228300541853254188973394324275526119409082151906335458925803081691961627262872909544911250939426559669641181741418792650389621395244191383680090126152455331128151622579879305128105513594663146479955290034772381144185556023460209436347971723223
#
# def clear_collection(db):
#     data = db.collection(u'messages')
#     for d in data.stream():
#         d.reference.delete()
#
# clear_collection(db)
# shutdown = False
# messages = []
#
# def receving(user_name):
#
#     while not shutdown:
#         read_ref = db.collection(u'messages')
#         read_ref = read_ref.where(u'user', u'!=', u'pashka-cheburashka')
#         for doc in read_ref.stream():
#             if doc.id not in messages:
#                 messages.append(doc.id)
#                 print(f"{doc.to_dict()[u'user']} => {doc.to_dict()[u'message'].decode('utf-8')}")
#         time.sleep(5)
#
#
#
#
# rT = threading.Thread(target=receving, args=(u'pashka-cheburashka', ))
# rT.start()
#
# while shutdown == False:
#     try:
#         message = input().encode('utf-8')
#         if message != "":
#             doc_ref = db.collection(u'messages').document(str(uuid.uuid4()))
#             doc_ref.set({u'message': message, u'user': u'pashka-cheburashka'})
#
#         #time.sleep(2)
#     except:
#         shutdown = True
#
# rT.join()
