from dynamodb_encryption_sdk.structures import AttributeActions, EncryptionContext

from cryptoshredding.dynamodb import encrypt_python_item, decrypt_python_item
from .. import create_in_memory_key_store


def test_decrypt_python_item():
    key_id = "key"
    key_store = create_in_memory_key_store()
    key_store.create_key(key_id)

    plaintext_item = {
        "example": "data",
        "some numbers": 99,
    }

    encrypted_attributes = set(plaintext_item.keys())

    encrypted_item = encrypt_python_item(
        item=plaintext_item,
        key_id=key_id,
        key_store=key_store,
        encryption_context=EncryptionContext(),
        attribute_actions=AttributeActions(),
    )

    decrypted_item = decrypt_python_item(
        item=encrypted_item,
        key_store=key_store,
        encryption_context=EncryptionContext(),
        attribute_actions=AttributeActions(),
    )

    for name in encrypted_attributes:
        assert encrypted_item[name] != plaintext_item[name]
        assert decrypted_item[name] == plaintext_item[name]
