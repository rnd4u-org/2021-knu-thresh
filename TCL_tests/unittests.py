from threshold_crypto import (ThresholdCrypto, ThresholdParameters)
import unittest


def encrypting_and_decrypting(key_params, threshold_params, message):
    pub_key, key_shares = ThresholdCrypto.create_public_key_and_shares_centralized(key_params, threshold_params)

    encrypted_message = ThresholdCrypto.encrypt_message(message, pub_key)
    reconstruct_shares = [key_shares[i] for i in [0, 2, 4]]
    partial_decryptions = [ThresholdCrypto.compute_partial_decryption(encrypted_message, share) for share in
                           reconstruct_shares]
    decrypted_message = ThresholdCrypto.decrypt_message(partial_decryptions, encrypted_message, threshold_params,
                                                        key_params)
    return decrypted_message


class TestEncrypting(unittest.TestCase):

    def test_latin(self):
        self.assertEqual(
            encrypting_and_decrypting(ThresholdCrypto.static_2048_key_parameters(), ThresholdParameters(3, 5), 'Secret message of Pavlo Pinchuk'),
            'Secret message of Pavlo Pinchuk')


    def test_cyrillic(self):
        self.assertEqual(
            encrypting_and_decrypting(ThresholdCrypto.static_1024_key_parameters(), ThresholdParameters(2, 5), 'Секретное послание Пинчука Павла'),
            'Секретное послание Пинчука Павла')


    def test_symbolic(self):
        self.assertEqual(
            encrypting_and_decrypting(ThresholdCrypto.generate_key_parameters(256), ThresholdParameters(3, 5), '$ecre! me&&a@e @f P@^!() P!n(huk'),
            '$ecre! me&&a@e @f P@^!() P!n(huk')


    def test_hieroglyphs(self):
        self.assertEqual(
            encrypting_and_decrypting(ThresholdCrypto.static_1024_key_parameters(), ThresholdParameters(3, 5), 'Paul Pinchuk의 비밀 메시지'),
            'Paul Pinchuk의 비밀 메시지')


    def test_special_symbolic(self):
        self.assertEqual(
            encrypting_and_decrypting(ThresholdCrypto.static_1024_key_parameters(), ThresholdParameters(3, 5), 'Secret message of Pavlo Pinchuk\u00a9'),
            'Secret message of Pavlo Pinchuk\u00a9')


    def test_long_message(self):
        self.assertEqual(
            encrypting_and_decrypting(ThresholdCrypto.static_1024_key_parameters(), ThresholdParameters(3, 5), 'Secret message of Pavlo Pinchuk' * 1000),
            'Secret message of Pavlo Pinchuk' * 1000)
