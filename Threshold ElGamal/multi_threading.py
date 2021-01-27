from threshold_crypto_lib import (ThresholdCrypto, ThresholdParameters)
import threading

def multi_threading(k, key_params, key_shares, threshold_params, encrypted_message, key_list):
    reconstruct_shares = [key_shares[i] for i in key_list]

    partial_decryptions = []

    def partial_decryption(share):
        part_decrypt = ThresholdCrypto.compute_partial_decryption(encrypted_message, share)
        partial_decryptions.append(part_decrypt)

    threads = []

    for i in range(k):
        thread = threading.Thread(target=partial_decryption, args=(reconstruct_shares[i],))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    decrypted_message = ThresholdCrypto.decrypt_message(partial_decryptions, encrypted_message, threshold_params,
                                                        key_params)
    return decrypted_message

key_params = ThresholdCrypto.static_2048_key_parameters()
thresh_params = ThresholdParameters(3, 5)
message = 'secret message 2002'
pub_key, key_shares = ThresholdCrypto.create_public_key_and_shares_centralized(key_params, thresh_params)

encrypted_message = ThresholdCrypto.encrypt_message(message, pub_key)
print(multi_threading(4, key_params, key_shares,
                      thresh_params, encrypted_message, [0, 1, 2, 3]))
