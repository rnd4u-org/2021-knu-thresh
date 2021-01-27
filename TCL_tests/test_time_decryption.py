from threshold_crypto import (ThresholdCrypto, ThresholdParameters)
import time

# Generate parameters, public key and shares
key_params = ThresholdCrypto.static_1024_key_parameters()
thresh_params = ThresholdParameters(3, 5)
pub_key, key_shares = ThresholdCrypto.create_public_key_and_shares_centralized(key_params, thresh_params)

# encrypt message using the public key
message = 'Secret message of Pavlo Pinchuk'
encrypted_message = ThresholdCrypto.encrypt_message(message, pub_key)

# build partial decryptions of three share owners using their shares
time.perf_counter()
reconstruct_shares = [key_shares[i] for i in [0, 2, 4]]
partial_decryptions = [ThresholdCrypto.compute_partial_decryption(encrypted_message, share) for share in
                       reconstruct_shares]

# combine these partial decryptions to recover the message
decrypted_message = ThresholdCrypto.decrypt_message(partial_decryptions, encrypted_message, thresh_params, key_params)
t = time.process_time()
print('Time of decryption: ', t, 'seconds')
print('Message: ', decrypted_message)
