""" Tests to encrypt a piece of data, then decrypt it and match with initial data
    using unittest library.
"""

import unittest
from threshold_crypto import (ThresholdCrypto, ThresholdParameters, ThresholdCryptoError)


def encrypt_decrypt(message, key_params, thresh_params, shares):

    pub_key, key_shares = ThresholdCrypto.create_public_key_and_shares_centralized(key_params, thresh_params)
    encrypted_message = ThresholdCrypto.encrypt_message(message, pub_key)

    reconstruct_shares = [key_shares[i] for i in shares]
    partial_decryptions = [ThresholdCrypto.compute_partial_decryption(encrypted_message, share) for share in
                           reconstruct_shares]
    decrypted_message = ThresholdCrypto.decrypt_message(partial_decryptions, encrypted_message, thresh_params,
                                                        key_params)
    return decrypted_message


class TestEncryptDecrypt(unittest.TestCase):

    def test_latin_and_symbols(self):
        message = "$Some@ #secret% &message* *to& %be# @encrypted$"
        key_params = ThresholdCrypto.static_2048_key_parameters()
        thresh_params = ThresholdParameters(3, 5)
        shares = (0, 2, 3)
        self.assertEqual(encrypt_decrypt(message, key_params, thresh_params, shares), message)

    def test_cyrillic(self):
        message = "Деяке повідомлення для шифрування"
        key_params = ThresholdCrypto.static_2048_key_parameters()
        thresh_params = ThresholdParameters(3, 5)
        shares = (0, 2, 3)
        self.assertEqual(encrypt_decrypt(message, key_params, thresh_params, shares), message)

    def test_new_key(self):
        message = "Some secret message to be encrypted"
        key_params = ThresholdCrypto.generate_key_parameters(128)
        thresh_params = ThresholdParameters(3, 5)
        shares = (0, 2, 3)
        self.assertEqual(encrypt_decrypt(message, key_params, thresh_params, shares), message)

    def test_long_message(self):
        message = "Some long secret message to be encrypted" * 10000
        key_params = ThresholdCrypto.static_2048_key_parameters()
        thresh_params = ThresholdParameters(3, 5)
        shares = (0, 2, 3)
        self.assertEqual(encrypt_decrypt(message, key_params, thresh_params, shares), message)

    def test_japanese(self):
        message = "暗号化されるいくつかの秘密のメッセージ"
        key_params = ThresholdCrypto.static_2048_key_parameters()
        thresh_params = ThresholdParameters(3, 5)
        shares = (0, 2, 3)
        self.assertEqual(encrypt_decrypt(message, key_params, thresh_params, shares), message)

    def test_less_shares(self):
        message = "暗号化されるいくつかの秘密のメッセージ"
        key_params = ThresholdCrypto.static_2048_key_parameters()
        thresh_params = ThresholdParameters(3, 5)
        shares = (0, 2, 2)
        with self.assertRaises(ThresholdCryptoError):
            encrypt_decrypt(message, key_params, thresh_params, shares)

    def test_more_shares(self):
        message = "暗号化されるいくつかの秘密のメッセージ"
        key_params = ThresholdCrypto.static_2048_key_parameters()
        thresh_params = ThresholdParameters(3, 6)
        shares = (0, 2, 3, 5)
        self.assertEqual(encrypt_decrypt(message, key_params, thresh_params, shares), message)

    def test_wrong_shares(self):
        message = "暗号化されるいくつかの秘密のメッセージ"

        key_params = ThresholdCrypto.static_2048_key_parameters()
        thresh_params = ThresholdParameters(3, 6)

        pub_key1, key_shares1 = ThresholdCrypto.create_public_key_and_shares_centralized(key_params, thresh_params)
        pub_key2, key_shares2 = ThresholdCrypto.create_public_key_and_shares_centralized(key_params, thresh_params)

        encrypted_message = ThresholdCrypto.encrypt_message(message, pub_key1)
        reconstruct_shares = [key_shares1[0], key_shares1[1], key_shares2[0]]

        with self.assertRaises(ThresholdCryptoError):
            partial_decryptions = [ThresholdCrypto.compute_partial_decryption(encrypted_message, share) for share in
                                   reconstruct_shares]
            decrypted_message = ThresholdCrypto.decrypt_message(partial_decryptions, encrypted_message, thresh_params,
                                                                key_params)



