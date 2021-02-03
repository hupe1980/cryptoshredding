from dynamodb_encryption_sdk.encrypted import CryptoConfig
from dynamodb_encryption_sdk.encrypted.item import (
    decrypt_dynamodb_item as aws_decrypt_dynamodb_item,
    encrypt_dynamodb_item as aws_encrypt_dynamodb_item,
)
from dynamodb_encryption_sdk.transform import ddb_to_dict, dict_to_ddb
from dynamodb_encryption_sdk.structures import AttributeActions, EncryptionContext


from ..key_store import KeyStore
from .materials_provider import KeyStoreMaterialsProvider


def encrypt_dynamodb_item(
    item,
    key_id: str,
    key_store: KeyStore,
    encryption_context: EncryptionContext,
    attribute_actions: AttributeActions,
):
    materials_provider = KeyStoreMaterialsProvider(
        key_store=key_store,
        material_description={"key_id": key_id},
    )
    crypto_config = CryptoConfig(
        materials_provider=materials_provider,
        encryption_context=encryption_context,
        attribute_actions=attribute_actions,
    )
    return aws_encrypt_dynamodb_item(item, crypto_config)


def encrypt_python_item(
    item,
    key_id: str,
    key_store: KeyStore,
    encryption_context: EncryptionContext,
    attribute_actions: AttributeActions,
):
    ddb_item = dict_to_ddb(item)
    encrypted_ddb_item = encrypt_dynamodb_item(
        item=ddb_item,
        key_id=key_id,
        key_store=key_store,
        encryption_context=encryption_context,
        attribute_actions=attribute_actions,
    )
    return ddb_to_dict(encrypted_ddb_item)


def decrypt_dynamodb_item(
    item,
    key_store: KeyStore,
    encryption_context: EncryptionContext,
    attribute_actions: AttributeActions,
):
    materials_provider = KeyStoreMaterialsProvider(
        key_store=key_store,
    )
    crypto_config = CryptoConfig(
        materials_provider=materials_provider,
        encryption_context=encryption_context,
        attribute_actions=attribute_actions,
    )
    return aws_decrypt_dynamodb_item(item, crypto_config)


def decrypt_python_item(
    item,
    key_store: KeyStore,
    encryption_context: EncryptionContext,
    attribute_actions: AttributeActions,
):
    ddb_item = dict_to_ddb(item)
    decrypted_ddb_item = decrypt_dynamodb_item(
        item=ddb_item,
        key_store=key_store,
        encryption_context=encryption_context,
        attribute_actions=attribute_actions,
    )
    return ddb_to_dict(decrypted_ddb_item)
