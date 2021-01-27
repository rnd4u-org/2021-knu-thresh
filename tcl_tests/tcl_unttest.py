""" Tests to encrypt a piece of data, then decrypt it and match with initial data
    using unittest library.
"""

import unittest
from threshold_crypto import (ThresholdCrypto, ThresholdParameters)


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

    def test1(self):
        message = "$Some@ #secret% &message* *to& %be# @encrypted$"
        key_params = ThresholdCrypto.static_2048_key_parameters()
        thresh_params = ThresholdParameters(3, 5)
        shares = (0, 2, 3)
        self.assertEqual(encrypt_decrypt(message, key_params, thresh_params, shares), message)

    def test2(self):
        message = "Деяке повідомлення для шифрування"
        key_params = ThresholdCrypto.static_2048_key_parameters()
        thresh_params = ThresholdParameters(3, 5)
        shares = (0, 2, 3)
        self.assertEqual(encrypt_decrypt(message, key_params, thresh_params, shares), message)

    def test3(self):
        message = "Some secret message to be encrypted"
        key_params = ThresholdCrypto.generate_key_parameters(128)
        thresh_params = ThresholdParameters(3, 5)
        shares = (0, 2, 3)
        self.assertEqual(encrypt_decrypt(message, key_params, thresh_params, shares), message)

    def test4(self):
        message = "Some long secret message to be encrypted" * 10000
        key_params = ThresholdCrypto.static_2048_key_parameters()
        thresh_params = ThresholdParameters(3, 5)
        shares = (0, 2, 3)
        self.assertEqual(encrypt_decrypt(message, key_params, thresh_params, shares), message)

    def test5(self):
        message = "暗号化されるいくつかの秘密のメッセージ"
        key_params = ThresholdCrypto.static_2048_key_parameters()
        thresh_params = ThresholdParameters(3, 5)
        shares = (0, 2, 3)
        self.assertEqual(encrypt_decrypt(message, key_params, thresh_params, shares), message)



