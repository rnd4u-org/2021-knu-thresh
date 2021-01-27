from threshold_crypto_lib import (ThresholdCrypto, ThresholdParameters)
import unittest


def decrypting(key_params, threshold_params, message):
    pub_key, key_shares = ThresholdCrypto.create_public_key_and_shares_centralized(key_params, threshold_params)

    encrypted_message = ThresholdCrypto.encrypt_message(message, pub_key)
    reconstruct_shares = [key_shares[i] for i in [0, 2, 4]]
    partial_decryptions = [ThresholdCrypto.compute_partial_decryption(encrypted_message, share) for share in
                           reconstruct_shares]
    decrypted_message = ThresholdCrypto.decrypt_message(partial_decryptions, encrypted_message, threshold_params,
                                                        key_params)
    return decrypted_message


class TestEncrypting(unittest.TestCase):

    def test1(self):
        self.assertEqual(
            decrypting(ThresholdCrypto.static_2048_key_parameters(), ThresholdParameters(3, 5), 'secret message'),
            'secret message')

    def test2(self):
        self.assertEqual(
            decrypting(ThresholdCrypto.static_1024_key_parameters(), ThresholdParameters(2, 5), 'секретне повідомлення'),
            'секретне повідомлення')

    def test3(self):
        self.assertEqual(
            decrypting(ThresholdCrypto.static_512_key_parameters(), ThresholdParameters(1, 5), '讚美太陽'),
            '讚美太陽')

    def test4(self):
        self.assertEqual(
            decrypting(ThresholdCrypto.static_512_key_parameters(), ThresholdParameters(1, 5), '0428 654'),
            '0428 654')

    def test5(self):
        self.assertEqual(
            decrypting(ThresholdCrypto.generate_key_parameters(512), ThresholdParameters(3, 5),
                                      '0428 654 їїї 讚美'), '0428 654 їїї 讚美')
