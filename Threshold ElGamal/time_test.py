from threshold_crypto_lib import (ThresholdCrypto, ThresholdParameters)
import time

key_params = ThresholdCrypto.static_1024_key_parameters()
thresh_params = ThresholdParameters(3, 5)
pub_key, key_shares = ThresholdCrypto.create_public_key_and_shares_centralized(key_params, thresh_params)

message = '0428 654 їїї 讚美'
encrypted_message = ThresholdCrypto.encrypt_message(message, pub_key)

time.perf_counter()

reconstruct_shares = [key_shares[i] for i in [0, 2, 4]]
partial_decryptions = [ThresholdCrypto.compute_partial_decryption(encrypted_message, share) for share in
                       reconstruct_shares]

decrypted_message = ThresholdCrypto.decrypt_message(partial_decryptions, encrypted_message, thresh_params, key_params)

t = time.process_time()
print('Time: ', t, 'seconds')
print('Message: ', decrypted_message)