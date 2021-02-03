from dynamodb_encryption_sdk.encrypted import CryptoConfig
from dynamodb_encryption_sdk.encrypted.item import decrypt_python_item, encrypt_python_item

from ..key_store import KeyStore
from .materials_provider import KeyStoreMaterialsProvider


def encrypt_item(item, key_id: str, key_store: KeyStore, encryption_context, attribute_actions):
    materials_provider = KeyStoreMaterialsProvider(
        key_store=key_store,
        material_description={"key_id": key_id},
    )
    crypto_config = CryptoConfig(
        materials_provider=materials_provider,
        encryption_context=encryption_context,
        attribute_actions=attribute_actions,
    )
    return encrypt_python_item(item, crypto_config)


def decrypt_item(item, key_store: KeyStore, encryption_context, attribute_actions):
    materials_provider = KeyStoreMaterialsProvider(
        key_store=key_store,
    )
    crypto_config = CryptoConfig(
        materials_provider=materials_provider,
        encryption_context=encryption_context,
        attribute_actions=attribute_actions,
    )
    return decrypt_python_item(item, crypto_config)
