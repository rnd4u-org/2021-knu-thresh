from threshold_crypto import (ThresholdCrypto, ThresholdParameters)

# Generate parameters, public key and shares
key_params = ThresholdCrypto.generate_key_parameters(512)
thresh_params = ThresholdParameters(3, 5)
pub_key, key_shares = ThresholdCrypto.create_public_key_and_shares_centralized(key_params, thresh_params)

# encrypt message using the public key
message = 'Some secret message to be encrypted!'
encrypted_message = ThresholdCrypto.encrypt_message(message, pub_key)

# build partial decryptions of three share owners using their shares
reconstruct_shares = [key_shares[i] for i in [0, 1, 3]]
partial_decryptions = [ThresholdCrypto.compute_partial_decryption(encrypted_message, share) for share in reconstruct_shares]

# combine these partial decryptions to recover the message
decrypted_message = ThresholdCrypto.decrypt_message(partial_decryptions, encrypted_message, thresh_params, key_params)
print(decrypted_message)
