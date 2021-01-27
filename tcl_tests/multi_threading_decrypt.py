"""  Applied multi-threading to decrypt t out of n pieces of data in parallel
"""

from threshold_crypto import (ThresholdCrypto, ThresholdParameters)
import threading


def decrypt_message_multi_threading(k, encrypted_message, shares, key_shares, thresh_params, key_params):

    partial_decryptions = []

    def part_decrypt(share):
        reconstruct_share = key_shares[share]
        partial_decryption = ThresholdCrypto.compute_partial_decryption(encrypted_message, reconstruct_share)
        partial_decryptions.append(partial_decryption)

    threads = []

    for i in range(k):
        thread = threading.Thread(target=part_decrypt, args=(shares[i], ))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    decrypted_message = ThresholdCrypto.decrypt_message(partial_decryptions, encrypted_message, thresh_params, key_params)

    return decrypted_message


# Generate parameters, public key and shares
key_params = ThresholdCrypto.static_512_key_parameters()
thresh_params = ThresholdParameters(3, 5)
pub_key, key_shares = ThresholdCrypto.create_public_key_and_shares_centralized(key_params, thresh_params)

# encrypt message using the public key
message = 'Some secret message to be encrypted!'
encrypted_message = ThresholdCrypto.encrypt_message(message, pub_key)

# build partial decryptions combine these partial decryptions to recover the message
decrypted_message = decrypt_message_multi_threading(3, encrypted_message, (0, 2, 1), key_shares, thresh_params, key_params)

