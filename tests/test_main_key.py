import os
import pytest
from cryptoshredding import MainKey


@pytest.fixture
def main_key():
    main_key = MainKey(
        key_id="key1",
        key_bytes=os.urandom(32),
    )
    yield main_key


def test_generate_data_key(main_key):
    data_key, encrypted_data_key = main_key.generate_data_key()

    decrypted_data_key = main_key.decrypt(encrypted_data_key)

    assert data_key != encrypted_data_key
    assert data_key == decrypted_data_key


def test_encrypt_decrypt(main_key):
    data_key = os.urandom(32)

    encrypted_data_key = main_key.encrypt(data_key)
    decrypted_data_key = main_key.decrypt(encrypted_data_key)

    assert data_key != encrypted_data_key
    assert data_key == decrypted_data_key


