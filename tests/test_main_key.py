import os
from cryptoshredding import MainKey


def test_data_key():
    main_key = MainKey(
        key_id="foo",
        key_bytes=os.urandom(32),
    )

    data_key, encrypted_data_key = main_key.generate_data_key()

    decrypted_data_key = main_key.decrypt(encrypted_data_key)

    assert data_key != encrypted_data_key
    assert data_key == decrypted_data_key
