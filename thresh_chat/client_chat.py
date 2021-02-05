import json, time
from threshold_crypto_lib import ThresholdParameters, KeyParameters, PublicKey, KeyShare, ThresholdCrypto, EncryptedMessage, PartialDecryption
import firebase_admin
from firebase_admin import firestore, credentials
import threading
import uuid


def prepare_crypto():

    def prepare_values_str_to_int(values):

        p = int(values[u'p'])
        q = int(values[u'q'])
        g = int(values[u'g'])
        n = values[u'n']
        t = values[u't']
        pub_key = int(values[u'pub_key'])
        share = [values[u'share'][0], int(values[u'share'][1])]
        return p, q, g, n, t, pub_key, share

    def regenerate_crypto_params_objects(p, q, g, n, t, pub_key, share):

        key_params = KeyParameters(p, q, g)
        thresh_params = ThresholdParameters(t, n)
        pub_key = PublicKey(pub_key, key_params)
        share = KeyShare(share[0], share[1], key_params)
        return key_params, thresh_params, pub_key, share

    with open('key_parameters.json') as file:
        key_parameters = json.load(file)

    p, q, g, n, t, pub_key, share = prepare_values_str_to_int(key_parameters)
    key_params, thresh_params, pub_key, share = regenerate_crypto_params_objects(p, q, g, n, t, pub_key, share)

    return key_params, thresh_params, pub_key, share


key_params, thresh_params, pub_key, share = prepare_crypto()

# ===================== setup =========================
cred = credentials.Certificate(r'C:\Users\User\Desktop\thresholdcryptochat-firebase-adminsdk-efq0t-9f4616190a.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
user_name = u'dmytro'

def clear_collection(db):
    data = db.collection(u'messages')
    for d in data.stream():
        d.reference.delete()
    # data = db.collection(u'parts')
    # for d in data.stream():
    #     d.reference.delete()

# clear_collection(db)

shutdown = False
messages = []
parts_id = []

callback_done = threading.Event()
read_ref = db.collection(u'messages')


def on_snapshot(collection_snapshot, changes, read_time):

    for doc in collection_snapshot:
        if doc.id not in messages:
            if doc.to_dict()[u'user'] != user_name:
                messages.append(doc.id)
                doc = doc.to_dict()
                encrypted_message = EncryptedMessage(int(doc[u'v']), int(doc[u'c']), doc[u'message'])

                partial_decryption = ThresholdCrypto.compute_partial_decryption(encrypted_message, share)
                x = partial_decryption.x
                v_y = str(partial_decryption.v_y)

                doc_ref = db.collection(u'parts').document(str(uuid.uuid4()))
                doc_ref.set({u'user': user_name, u'x': x, u'v_y': v_y})
                time.sleep(2)

                partial_decryptions = []
                read_ref2 = db.collection(u'parts')
                for part in read_ref2.stream():
                    #if part.id not in parts_id:
                    #parts_id.append(part.id)
                    part = part.to_dict()
                    part_decryption = PartialDecryption(part[u'x'], int(part[u'v_y']))
                    partial_decryptions.append(part_decryption)



                decrypted_message = ThresholdCrypto.decrypt_message(partial_decryptions, encrypted_message,
                                                                    thresh_params, key_params)
                print(decrypted_message)
            # else:
            #     time.sleep(2)
            #     read_ref2 = db.collection(u'parts')
            #     for part in read_ref2.stream():
            #         if part.id not in parts_id:
            #             parts_id.append(part.id)

    callback_done.set()


query_watch = read_ref.on_snapshot(on_snapshot)

while shutdown == False:
    try:
        message = input()
        if message != "":
            encrypted = ThresholdCrypto.encrypt_message(message, pub_key)
            encrypted_message = encrypted.enc
            v = str(encrypted.v)
            c = str(encrypted.c)

            doc_ref = db.collection(u'messages').document(str(uuid.uuid4()))
            data = db.collection(u'parts')
            for d in data.stream():
                d.reference.delete()
            doc_ref.set({u'user': user_name, u'message': encrypted_message, u'v': v, u'c': c})
    except:
        shutdown = True
