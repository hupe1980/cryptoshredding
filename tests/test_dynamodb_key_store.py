import os

import boto3
from moto import mock_dynamodb2
from dynamodb_encryption_sdk.delegated_keys.jce import JceNameLocalDelegatedKey
from dynamodb_encryption_sdk.material_providers.wrapped import WrappedCryptographicMaterialsProvider
from dynamodb_encryption_sdk.identifiers import EncryptionKeyType, KeyEncodingType

from cryptoshredding import DynamodbKeyStore


@mock_dynamodb2
def test_key_generation():
    table_name = "key_store"

    DynamodbKeyStore.create_table(
        client=boto3.client("dynamodb", region_name="us-east-1"),
        table_name=table_name,
    )

    table = boto3.resource("dynamodb", region_name="us-east-1").Table(table_name)

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

    key_store = DynamodbKeyStore(table=table, materials_provider=wrapped_cmp)

    key_id = "key1"
    new_main_key = key_store.create_main_key(key_id)
    main_key = key_store.get_main_key(key_id)

    assert main_key.key_id == new_main_key.key_id
    assert main_key.key_bytes == new_main_key.key_bytes
