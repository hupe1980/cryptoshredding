import boto3
from moto import mock_dynamodb2
from dynamodb_encryption_sdk.identifiers import CryptoAction
from dynamodb_encryption_sdk.structures import AttributeActions

from cryptoshredding.dynamodb.table import CryptoTable
from .. import create_in_memory_key_store

table_name = "dummy"


@mock_dynamodb2
def test_get_item():
    dynamodb = boto3.resource("dynamodb")

    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            },

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )

    key_id = "foo"
    key_store = create_in_memory_key_store()
    key_store.create_key(key_id=key_id)

    index_key = {"id": "bar"}
    plaintext_item = {
        "example": "data",
        "some numbers": 99,
        "ignore": "no encryption",
    }

    encrypted_attributes = set(plaintext_item.keys())
    encrypted_attributes.remove("ignore")
    unencrypted_attributes = set(index_key.keys())
    unencrypted_attributes.add("ignore")

    plaintext_item.update(index_key)

    actions = AttributeActions(
        default_action=CryptoAction.ENCRYPT_AND_SIGN,
        attribute_actions={
            "ignore": CryptoAction.DO_NOTHING,
        }
    )

    crypto_table = CryptoTable(
        table=table,
        key_store=key_store,
        attribute_actions=actions,
    )
    crypto_table.put_item(key_id=key_id, Item=plaintext_item)

    encrypted_item = table.get_item(Key=index_key)["Item"]
    decrypted_item = crypto_table.get_item(Key=index_key)["Item"]

    for name in encrypted_attributes:
        assert encrypted_item[name] != plaintext_item[name]
        assert decrypted_item[name] == plaintext_item[name]

    for name in unencrypted_attributes:
        assert decrypted_item[name] == encrypted_item[name] == plaintext_item[name]
