import os

from dynamodb_encryption_sdk.delegated_keys.jce import JceNameLocalDelegatedKey
from dynamodb_encryption_sdk.material_providers.wrapped import WrappedCryptographicMaterialsProvider
from dynamodb_encryption_sdk.identifiers import EncryptionKeyType, KeyEncodingType

from cryptoshredding.in_memory_key_store import InMemoryKeyStore


def create_in_memory_key_store():
    key_bytes = os.urandom(32)

    wrapping_key = JceNameLocalDelegatedKey(
        key=key_bytes,
        algorithm="AES",
        key_type=EncryptionKeyType.SYMMETRIC,
        key_encoding=KeyEncodingType.RAW,
    )
    signing_key = JceNameLocalDelegatedKey(
        key=key_bytes,
        algorithm="HmacSHA512",
        key_type=EncryptionKeyType.SYMMETRIC,
        key_encoding=KeyEncodingType.RAW,
    )
    wrapped_cmp = WrappedCryptographicMaterialsProvider(
        wrapping_key=wrapping_key,
        unwrapping_key=wrapping_key,
        signing_key=signing_key,
    )

    key_store = InMemoryKeyStore(materials_provider=wrapped_cmp)

    return key_store
