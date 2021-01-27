import time
from threshold_crypto import (ThresholdCrypto,
                              ThresholdParameters
                              )

def test_encryption(message):
    key_params = ThresholdCrypto.static_1024_key_parameters()
    thresh_params = ThresholdParameters(3, 7)

    pub_key, key_shares = ThresholdCrypto.create_public_key_and_shares_centralized(key_params, thresh_params)
    encrypted_message = ThresholdCrypto.encrypt_message(message, pub_key)
    reconstruct_shares = [key_shares[i] for i in [1, 3, 5]]

    return encrypted_message, reconstruct_shares, thresh_params, key_params


def test_decryption(encrypted_message, reconstruct_shares, thresh_params, key_params):

    partial_decryptions = [ThresholdCrypto.compute_partial_decryption(encrypted_message, share) for share in
                           reconstruct_shares]
    decrypted_message = ThresholdCrypto.decrypt_message(partial_decryptions, encrypted_message, thresh_params,
                                                        key_params)
    return decrypted_message


def test_decryption_time(encrypted_message, reconstruct_shares, thresh_params, key_params):
    start_time = time.time()

    partial_decryptions = [ThresholdCrypto.compute_partial_decryption(encrypted_message, share) for share in
                           reconstruct_shares]
    decrypted_message = ThresholdCrypto.decrypt_message(partial_decryptions, encrypted_message, thresh_params,
                                                        key_params)

    end_time = (time.time() - start_time) * 1000
    return decrypted_message, end_time

messages = [
    "hello",
    "World",
    "123654789",
    "I have a lot of things today, so I’ll go in first ",
    "Okey"
    ]

for message in messages:
    encrypted_message, reconstruct_shares, thresh_params, key_params = test_encryption(message)
    test = test_decryption(encrypted_message, reconstruct_shares, thresh_params, key_params)
    if message == test:
        print(test)

message = "Jinwoo, who gave a smile to a partner who had funnyly saluting, got out of the office with his coat hanging on the chair ."


encrypted_message, reconstruct_shares, thresh_params, key_params = test_encryption(message)

decrypted, time_ = test_decryption_time(encrypted_message, reconstruct_shares, thresh_params, key_params)

print("\n {},\n {} mSec".format(decrypted, time_))