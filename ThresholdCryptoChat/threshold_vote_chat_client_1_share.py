"""
The Main Idea of the Chat.
- Exist 4 static members of community.
One of members creates a message and encrypts it by public key of the Threshold crypto-scheme
- This member sends the message with ID to other members.
To show this message, each (at least 2 of 4 - according to threshold scheme requirements)
member should use own key to prepare own part of the decrypted message and send it to other members.
- Our Threshold crypto-scheme is hierarchical, Pasha has two key shares
- Each member unites all parts from other members and try to decrypt and read the message.
"""

import json, time
from threshold_crypto import *
import firebase_admin
from firebase_admin import firestore, credentials
import threading
import uuid
import tkinter as tk
from tkinter import messagebox as mb


def prepare_crypto():
    """
        Read all necessary crypto parameters for current chat session from 'key_parameters.json' file
        Convert all crypto parameters to necessary types
        :return: key_params, thresh_params, pub_key, share (are instances of correct types)
        """

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


def clear_collection(db):

    data = db.collection(u'messages_id')
    for d in data.stream():
        d.reference.delete()
    data = db.collection(u'parts')
    for d in data.stream():
        d.reference.delete()


def mLogin():

    global login
    login = tk.Toplevel()
    login.resizable(width=False, height=False)
    login.configure(width=400, height=250)
    pls = tk.Label(login, text="Welcome to Vote Crypto chat!\nEnter your username:", justify=tk.CENTER,
                   font="Helvetica 14 bold")
    pls.place(relheight=0.2, relx=0.15, rely=0.1)
    lName = tk.Label(login, text="Username: ", font="Helvetica 12")
    lName.place(relheight=0.15, relx=0.1, rely=0.32)
    eName = tk.Entry(login, font="Helvetica 14")
    eName.place(relwidth=0.4, relheight=0.1, relx=0.35, rely=0.35)
    eName.focus()
    log = tk.Button(login, text="Login", font="Helvetica 14 bold", command=lambda: logIn(eName.get()))
    log.place(relx=0.4, rely=0.55)


def logIn(name):

    global user_name
    login.destroy()
    user_name = name
    layout(name)


def layout(name):

    global textCons
    global entryMsg

    win.deiconify()
    win.title("Threshold Crypto Chat")
    win.resizable(width=False, height=False)
    win.configure(width=470, height=550, bg="#17202A")
    labelHead = tk.Label(win, bg="#17202A", fg="#EAECEE", text=name, font="Helvetica 13 bold", pady=5)
    labelHead.place(relwidth=1)
    line = tk.Label(win, width=450, bg="#ABB2B9")
    line.place(relwidth=1, rely=0.07, relheight=0.012)
    textCons = tk.Text(win, width=20, height=2, bg="#17202A", fg="#EAECEE", font="Helvetica 14", padx=5, pady=5)
    textCons.place(relheight=0.745, relwidth=1, rely=0.08)
    labelBottom = tk.Label(win, bg="#ABB2B9", height=80)
    labelBottom.place(relwidth=1, rely=0.825)
    entryMsg = tk.Entry(labelBottom, bg="#2C3E50", fg="#EAECEE", font="Helvetica 13")

    entryMsg.place(relwidth=0.74, relheight=0.06, rely=0.008, relx=0.011)
    entryMsg.focus()

    buttonMsg = tk.Button(labelBottom, text="Send", font="Helvetica 10 bold", width=20, bg="#ABB2B9",
                          command=lambda: sendButton(entryMsg.get()))
    buttonMsg.place(relx=0.77, rely=0.008, relheight=0.06, relwidth=0.22)
    textCons.config(cursor="arrow")

    scrollbar = tk.Scrollbar(textCons)

    scrollbar.place(relheight=1, relx=0.974)
    scrollbar.config(command=textCons.yview)
    textCons.config(state=tk.DISABLED)


def sendButton(message):

    global doc_ref
    global user_name
    global entryMsg
    entryMsg.delete(0, tk.END)

    try:
        if message != "":

            # Each raw message is encrypted by public key
            encrypted = ThresholdCrypto.encrypt_message(message, pub_key)
            encrypted_message = encrypted.enc
            v = str(encrypted.v)
            c = str(encrypted.c)

            doc_ref = db.collection(u'messages_id').document(str(uuid.uuid4()))

            data = db.collection(u'parts')
            for d in data.stream():
                d.reference.delete()

            doc_ref.set({u'user': user_name, u'message': encrypted_message, u'v': v, u'c': c})
            showMessage(message, user_name)
    except:
        pass


def on_snapshot(collection_snapshot, changes, read_time):
    """
    Read a new message from the firestore db.

    Each user may agree or disagree to decrypt the current message

    If user agree to decrypt the message, he prepares his own part and send it to the group
    Other users read all parts and try to read the message

    If number of agreed users more than threshold each user could see the raw message,
    otherwise each user sees "Access Denied"

    If user disagree to decrypt the message he sees "The message from {sender} won't be displayed"
    """
    for doc in collection_snapshot:
        if doc.id not in messages_id:

            if doc.to_dict()[u'user'] != user_name:
                t1 = time.perf_counter()
                want_to_read = wantToRead()
                t2 = time.perf_counter()
                if want_to_read and float(t2-t1) < 6:
                    messages_id.add(doc.id)
                    doc = doc.to_dict()
                    encrypted_message = EncryptedMessage(int(doc[u'v']), int(doc[u'c']), doc[u'message'])

                    partial_decryption = ThresholdCrypto.compute_partial_decryption(encrypted_message, share)
                    x = partial_decryption.x
                    v_y = str(partial_decryption.v_y)

                    doc_ref = db.collection(u'parts').document(str(uuid.uuid4()))
                    doc_ref.set({u'user': user_name, u'x': x, u'v_y': v_y})
                    time.sleep(5)

                    partial_decryptions = []
                    read_ref2 = db.collection(u'parts')

                    for part in read_ref2.stream():
                        part = part.to_dict()
                        part_decryption = PartialDecryption(part[u'x'], int(part[u'v_y']))
                        partial_decryptions.append(part_decryption)

                    try:
                        decrypted_message = ThresholdCrypto.decrypt_message(partial_decryptions, encrypted_message,
                                                                            thresh_params, key_params)
                        showMessage(decrypted_message, doc[u'user'])
                    except:
                        showMessage("Access Denied", doc[u'user'])

                else:
                    messages_id.add(doc.id)
                    showMessage(f"The message from {doc.to_dict()[u'user']} won't be displayed", user_name)

    callback_done.set()


def wantToRead():
    return mb.askyesno(title="New Message", message="Would you like to recieve?")


def showMessage(message, name):

    global textCons
    to_show = f'{name}: {message}'
    textCons.config(state=tk.NORMAL)
    textCons.insert(tk.END, to_show + "\n\n")
    textCons.config(state=tk.DISABLED)
    textCons.see(tk.END)


# ===================== start chat =========================

cred = credentials.Certificate(r'C:\GAMES\SecretFolder\votechatcrypto-firebase-adminsdk-qr0f2-6de712738a.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
clear_collection(db)

key_params, thresh_params, pub_key, share = prepare_crypto()

win = tk.Tk()
win.withdraw()
login = None
user_name = None
mLogin()

messages_id = set()

callback_done = threading.Event()
read_ref = db.collection(u'messages_id')

query_watch = read_ref.on_snapshot(on_snapshot)

win.mainloop()