"""  Tests to measure decryption speed (in mSec)
     tested parameters: different key sizes (512, 2048),                3-out-of-5
                        different message length (35, 35_000 symbols),  3-out-of-5
                        with & without multi-threading                  3-out-of-5
                        const 2048 key, short message; different t=  (3,8)-out-of-10

     Summary: decryption speed depends on key size and t-value; does not depend on message length
     ?! multi-threading

"""

from threshold_crypto import (ThresholdCrypto, ThresholdParameters)
from multi_threading_decrypt import decrypt_message_multi_threading


def benchmark(func):
    import time

    def wrapper(*args, **kwargs):
        start = time.time()
        return_value = func(*args, **kwargs)
        end = time.time()
        print(f'Execution time for {func.__name__} function: {(end-start) * 1000} mSec')
        return return_value

    return wrapper


@benchmark
def decrypt_message(encrypted_message, shares, key_shares, thresh_params, key_params):

    # build partial decryptions of three share owners using their shares
    reconstruct_shares = [key_shares[i] for i in shares]
    partial_decryptions = [ThresholdCrypto.compute_partial_decryption(encrypted_message, share) for share in
                           reconstruct_shares]

    # combine these partial decryptions to recover the message
    decrypted_message = ThresholdCrypto.decrypt_message(partial_decryptions, encrypted_message, thresh_params,key_params)

    return decrypted_message


@benchmark
def decrypt_message_multi_threading_(t, encrypted_message, shares, key_shares, thresh_params, key_params):
    decrypt_message_multi_threading(t, encrypted_message, shares, key_shares, thresh_params, key_params)


def TestCase_short_512_no_multi_threading():

    key_params = ThresholdCrypto.static_512_key_parameters()
    thresh_params = ThresholdParameters(3, 5)
    pub_key, key_shares = ThresholdCrypto.create_public_key_and_shares_centralized(key_params, thresh_params)

    message = 'Some secret message to be encrypted!'
    encrypted_message = ThresholdCrypto.encrypt_message(message, pub_key)

    print("TestCase_short_512_no_multi_threading")
    decrypt_message(encrypted_message, (0, 2, 3), key_shares, thresh_params, key_params)
    print()


def TestCase_short_2048_no_multi_threading():

    key_params = ThresholdCrypto.static_2048_key_parameters()
    thresh_params = ThresholdParameters(3, 5)
    pub_key, key_shares = ThresholdCrypto.create_public_key_and_shares_centralized(key_params, thresh_params)

    message = 'Some secret message to be encrypted!'
    encrypted_message = ThresholdCrypto.encrypt_message(message, pub_key)

    print("TestCase_short_2048_no_multi_threading")
    decrypt_message(encrypted_message, (0, 2, 3), key_shares, thresh_params, key_params)
    print()


def TestCase_long_512_no_multi_threading():

    key_params = ThresholdCrypto.static_512_key_parameters()
    thresh_params = ThresholdParameters(3, 5)
    pub_key, key_shares = ThresholdCrypto.create_public_key_and_shares_centralized(key_params, thresh_params)

    message = 'Some secret message to be encrypted!'*1000
    encrypted_message = ThresholdCrypto.encrypt_message(message, pub_key)

    print("TestCase_long_512_no_multi_threading")
    decrypt_message(encrypted_message, (0, 2, 3), key_shares, thresh_params, key_params)
    print()


def TestCase_long_2048_no_multi_threading():

    key_params = ThresholdCrypto.static_2048_key_parameters()
    thresh_params = ThresholdParameters(3, 5)
    pub_key, key_shares = ThresholdCrypto.create_public_key_and_shares_centralized(key_params, thresh_params)

    message = 'Some secret message to be encrypted!'*1000
    encrypted_message = ThresholdCrypto.encrypt_message(message, pub_key)

    print("TestCase_long_2048_no_multi_threading")
    decrypt_message(encrypted_message, (0, 2, 3), key_shares, thresh_params, key_params)
    print()


def TestCase_short_2048_no_multi_threading_3_outof_10():

    key_params = ThresholdCrypto.static_2048_key_parameters()
    thresh_params = ThresholdParameters(3, 10)
    pub_key, key_shares = ThresholdCrypto.create_public_key_and_shares_centralized(key_params, thresh_params)

    message = 'Some secret message to be encrypted!'
    encrypted_message = ThresholdCrypto.encrypt_message(message, pub_key)

    print("TestCase_short_2048_no_multi_threading_3_outof_10")
    decrypt_message(encrypted_message, (0, 2, 3), key_shares, thresh_params, key_params)
    print()


def TestCase_short_2048_no_multi_threading_8_outof_10():

    key_params = ThresholdCrypto.static_2048_key_parameters()
    thresh_params = ThresholdParameters(8, 10)
    pub_key, key_shares = ThresholdCrypto.create_public_key_and_shares_centralized(key_params, thresh_params)

    message = 'Some secret message to be encrypted!'
    encrypted_message = ThresholdCrypto.encrypt_message(message, pub_key)

    print("TestCase_short_2048_no_multi_threading_8_outof_10")
    decrypt_message(encrypted_message, (0, 1, 2, 3, 4, 5, 6, 7), key_shares, thresh_params, key_params)
    print()


def TestCase_short_512_multi_threading():

    key_params = ThresholdCrypto.static_512_key_parameters()
    thresh_params = ThresholdParameters(3, 5)
    pub_key, key_shares = ThresholdCrypto.create_public_key_and_shares_centralized(key_params, thresh_params)

    message = 'Some secret message to be encrypted!'
    encrypted_message = ThresholdCrypto.encrypt_message(message, pub_key)

    print("TestCase_short_512_multi_threading")
    decrypt_message_multi_threading_(thresh_params.t, encrypted_message, (0, 2, 3), key_shares, thresh_params, key_params)
    print()

def TestCase_long_512_multi_threading():

    key_params = ThresholdCrypto.static_512_key_parameters()
    thresh_params = ThresholdParameters(3, 5)
    pub_key, key_shares = ThresholdCrypto.create_public_key_and_shares_centralized(key_params, thresh_params)

    message = 'Some secret message to be encrypted!'*1000
    encrypted_message = ThresholdCrypto.encrypt_message(message, pub_key)

    print("TestCase_long_512_multi_threading")
    decrypt_message_multi_threading_(thresh_params.t, encrypted_message, (0, 2, 3), key_shares, thresh_params, key_params)
    print()

def TestCase_short_2048_multi_threading():

    key_params = ThresholdCrypto.static_2048_key_parameters()
    thresh_params = ThresholdParameters(3, 5)
    pub_key, key_shares = ThresholdCrypto.create_public_key_and_shares_centralized(key_params, thresh_params)

    message = 'Some secret message to be encrypted!'
    encrypted_message = ThresholdCrypto.encrypt_message(message, pub_key)

    print("TestCase_short_2048_multi_threading")
    decrypt_message_multi_threading_(thresh_params.t, encrypted_message, (0, 2, 3), key_shares, thresh_params, key_params)
    print()

def TestCase_long_2048_multi_threading():


    key_params = ThresholdCrypto.static_2048_key_parameters()
    thresh_params = ThresholdParameters(3, 5)
    pub_key, key_shares = ThresholdCrypto.create_public_key_and_shares_centralized(key_params, thresh_params)

    message = 'Some secret message to be encrypted!'*1000
    encrypted_message = ThresholdCrypto.encrypt_message(message, pub_key)

    print("TestCase_long_2048_multi_threading")
    decrypt_message_multi_threading_(thresh_params.t, encrypted_message, (0, 2, 3), key_shares, thresh_params, key_params)
    print()


TestCase_short_512_no_multi_threading()
TestCase_long_512_no_multi_threading()
TestCase_short_2048_no_multi_threading()
TestCase_long_2048_no_multi_threading()
TestCase_short_2048_no_multi_threading_3_outof_10()
TestCase_short_2048_no_multi_threading_8_outof_10()
print()
TestCase_short_512_multi_threading()
TestCase_short_2048_multi_threading()




