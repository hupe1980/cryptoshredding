import os

import boto3
from moto import mock_dynamodb2
from dynamodb_encryption_sdk.delegated_keys.jce import JceNameLocalDelegatedKey
from dynamodb_encryption_sdk.material_providers.wrapped import WrappedCryptographicMaterialsProvider
from dynamodb_encryption_sdk.identifiers import EncryptionKeyType, KeyEncodingType

from cryptoshredding.dynamodb_key_store import DynamodbKeyStore

table_name = "dummy_table"


@mock_dynamodb2
def test_key_generation():
    dynamodb = boto3.resource("dynamodb")

    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'key_id',
                'KeyType': 'HASH'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'key_id',
                'AttributeType': 'S'
            },

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )
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
        wrapping_key=wrapping_key, unwrapping_key=wrapping_key, signing_key=signing_key
    )

    key_store = DynamodbKeyStore(table=table, materials_provider=wrapped_cmp)
    new_key = key_store.create_key(key_id="foo")
    key = key_store.get_key(key_id="foo")

    assert key == new_key
