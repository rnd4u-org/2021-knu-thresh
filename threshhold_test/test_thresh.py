import time
from threshold_crypto import (ThresholdCrypto,
                               ThresholdParameters,
                               KeyParameters,
                               PublicKey,
                               KeyShare,
                               ThresholdCryptoError,
                               EncryptedMessage,
                               PartialDecryption,
                               )

def test(message):
    key_params = ThresholdCrypto.static_2048_key_parameters()

    thresh_params = ThresholdParameters(3, 5)

    pub_key, key_shares = ThresholdCrypto.create_public_key_and_shares_centralized(key_params, thresh_params)
    encrypted_message = ThresholdCrypto.encrypt_message(message, pub_key)
    reconstruct_shares = [key_shares[i] for i in [0, 2, 4]]
    partial_decryptions = [ThresholdCrypto.compute_partial_decryption(encrypted_message, share) for share in reconstruct_shares]
    decrypted_message = ThresholdCrypto.decrypt_message(partial_decryptions, encrypted_message, thresh_params, key_params)
    return decrypted_message

messages = [
    "message 1",
    "this is message 2",
    "message message message",
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaddddddddddddddffffffffffffff",
    "mmmmmmeeeeeeeeeessssssssssssaaaaaaaaagggggggggeeeee"
    ]

for message in messages:
    print(test(message))

message = "New message to measure decrypting time"

def testTime(message):
    key_params = ThresholdCrypto.static_2048_key_parameters()
    thresh_params = ThresholdParameters(3, 5)
    pub_key, key_shares = ThresholdCrypto.create_public_key_and_shares_centralized(key_params, thresh_params)
    encrypted_message = ThresholdCrypto.encrypt_message(message, pub_key)
    reconstruct_shares = [key_shares[i] for i in [0, 2, 4]]
    start_time = time.time()
    partial_decryptions = [ThresholdCrypto.compute_partial_decryption(encrypted_message, share) for share in reconstruct_shares]
    decrypted_message = ThresholdCrypto.decrypt_message(partial_decryptions, encrypted_message, thresh_params, key_params)
    end_time = (time.time() - start_time) * 1000
    return decrypted_message, end_time

decrypted, time_ = testTime(message)
print("{}, {} mSec".format(decrypted, time_))