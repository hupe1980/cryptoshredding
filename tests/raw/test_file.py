import os
import pytest
from pyfakefs.fake_filesystem_unittest import Patcher
from cryptoshredding.raw import CryptoFile
from .. import create_in_memory_key_store

Patcher.SKIPMODULES.add(pytest)
key_id = "key1"


@pytest.fixture
def key_store():
    key_store = create_in_memory_key_store()
    key_store.create_main_key(key_id)
    yield key_store


@pytest.fixture
def fs(request):
    """ Fake filesystem. """
    if hasattr(request, 'param'):
        # pass optional parameters via @pytest.mark.parametrize
        patcher = Patcher(*request.param)
    else:
        patcher = Patcher()
    patcher.setUp()
    yield patcher.fs
    patcher.tearDown()


def test_file(key_store, fs):
    text = "foo bar"
    with open("plain.txt", "w") as plaintext:
        plaintext.write(text)

    crypto_file = CryptoFile(
        key_store=key_store,
    )

    crypto_file.encrypt(
        key_id=key_id,
        plaintext_filename="plain.txt",
        ciphertext_filename="cipher.txt"
    )

    crypto_file.decrypt(
        ciphertext_filename="cipher.txt",
        plaintext_filename="decrypt.txt",
    )

    with open("cipher.txt", "rb") as encrypted:
        encrypted_text = encrypted.read()

    with open("decrypt.txt", "r") as decrypted:
        decrypted_text = decrypted.read()

    assert os.path.exists('plain.txt')
    assert os.path.exists('cipher.txt')
    assert os.path.exists('decrypt.txt')

    assert text != encrypted_text
    assert text == decrypted_text
