"""Tests to encrypt a piece of data, then decrypt it and match with initial data
    using doctest library
"""

import doctest
from threshold_crypto import (ThresholdCrypto, ThresholdParameters)


def encrypt_decrypt(message, key_params, thresh_params, shares):

    """
    Encrypt and decrypt message using threshold_crypto library

    >>> encrypt_decrypt('$Some@ #secret% &message* *to& %be# @encrypted$',\
                        ThresholdCrypto.static_2048_key_parameters(),\
                        ThresholdParameters(3, 5),\
                        (0, 2, 3))
    '$Some@ #secret% &message* *to& %be# @encrypted$'

    >>> encrypt_decrypt('Деяке повідомлення для шифрування',\
                        ThresholdCrypto.static_2048_key_parameters(),\
                        ThresholdParameters(3, 5),\
                        (0, 2, 3))
    'Деяке повідомлення для шифрування'

    >>> encrypt_decrypt('Some secret message to be encrypted',\
                        ThresholdCrypto.generate_key_parameters(128),\
                        ThresholdParameters(3, 5),\
                        (0, 2, 3))
    'Some secret message to be encrypted'

    >>> encrypt_decrypt('暗号化されるいくつかの秘密のメッセージ',\
                        ThresholdCrypto.static_2048_key_parameters(),\
                        ThresholdParameters(3, 5),\
                        (0, 2, 3))
    '暗号化されるいくつかの秘密のメッセージ'
    """

    pub_key, key_shares = ThresholdCrypto.create_public_key_and_shares_centralized(key_params, thresh_params)
    encrypted_message = ThresholdCrypto.encrypt_message(message, pub_key)

    reconstruct_shares = [key_shares[i] for i in shares]
    partial_decryptions = [ThresholdCrypto.compute_partial_decryption(encrypted_message, share) for share in
                           reconstruct_shares]
    decrypted_message = ThresholdCrypto.decrypt_message(partial_decryptions, encrypted_message, thresh_params,
                                                        key_params)
    return decrypted_message
