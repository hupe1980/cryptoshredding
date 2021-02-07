import pytest
from cryptoshredding.raw import CryptoString
from .. import create_in_memory_key_store


key_id = "key1"


@pytest.fixture
def key_store():
    key_store = create_in_memory_key_store()
    key_store.create_main_key(key_id)
    yield key_store


def test_string(key_store):
    source = "foo bar"

    crypto_string = CryptoString(
        key_store=key_store,
    )

    cypher_text, encrypted_header = crypto_string.encrypt(
        key_id=key_id,
        source=source,
    )

    plain_text, decrypted_header = crypto_string.decrypt(
        source=cypher_text,
    )

    assert cypher_text != source
    assert plain_text == source

    assert all(
        pair in decrypted_header.encryption_context.items() for pair in encrypted_header.encryption_context.items()
    )
