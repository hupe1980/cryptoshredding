import pytest
from cryptoshredding.raw import CryptoBytes
from .. import create_in_memory_key_store


key_id = "key1"


@pytest.fixture
def key_store():
    key_store = create_in_memory_key_store()
    key_store.create_main_key(key_id)
    yield key_store


def test_string(key_store):
    plain = b"foo bar"

    crypto_bytes = CryptoBytes(
        key_store=key_store,
    )

    encrypted, encrypted_header = crypto_bytes.encrypt(
        key_id=key_id,
        data=plain,
    )

    decrypted, decrypted_header = crypto_bytes.decrypt(
        data=encrypted,
    )

    assert plain != encrypted
    assert plain == decrypted

    assert all(
        pair in decrypted_header.encryption_context.items() for pair in encrypted_header.encryption_context.items()
    )
