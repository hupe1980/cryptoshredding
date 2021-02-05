import boto3
from boto3.dynamodb.conditions import Key
import pytest
from moto import mock_dynamodb2
from dynamodb_encryption_sdk.identifiers import CryptoAction
from dynamodb_encryption_sdk.structures import AttributeActions

from cryptoshredding.dynamodb import CryptoTable

from .. import create_in_memory_key_store


@pytest.fixture
def dynamodb():
    with mock_dynamodb2():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        yield dynamodb


@pytest.fixture
def table(dynamodb):
    table = dynamodb.create_table(
        TableName="dummy",
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
    return table


def test_get_item(table):
    key_id = "key"
    key_store = create_in_memory_key_store()
    key_store.create_key(key_id)

    index_key = {"id": "foo"}
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

    key_store.delete_key(key_id)

    with pytest.raises(Exception):
        decrypted_item = crypto_table.get_item(Key=index_key)["Item"]


def test_query(table):
    key_id = "key"
    key_store = create_in_memory_key_store()
    key_store.create_key(key_id)

    index_key = {"id": "foo"}
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

    encrypted_items = table.query(
        KeyConditionExpression=Key("id").eq("foo")
    )["Items"]
    decrypted_items = crypto_table.query(
        KeyConditionExpression=Key("id").eq("foo")
    )["Items"]

    assert len(encrypted_items) == 1
    assert len(decrypted_items) == 1

    for name in encrypted_attributes:
        assert encrypted_items[0][name] != plaintext_item[name]
        assert decrypted_items[0][name] == plaintext_item[name]

    for name in unencrypted_attributes:
        assert decrypted_items[0][name] == encrypted_items[0][name] == plaintext_item[name]

    # shredding
    key_store.delete_key(key_id)

    encrypted = table.query(
        KeyConditionExpression=Key("id").eq("foo")
    )
    decrypted = crypto_table.query(
        KeyConditionExpression=Key("id").eq("foo")
    )

    assert encrypted["Count"] == 1
    assert len(encrypted["Items"]) == 1

    assert decrypted["Count"] == 0
    assert len(decrypted["Items"]) == 0


def test_scan(table):
    key_id = "key"
    key_store = create_in_memory_key_store()
    key_store.create_key(key_id)

    index_key = {"id": "foo"}
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

    encrypted_items = table.scan()["Items"]
    decrypted_items = crypto_table.scan()["Items"]

    assert len(encrypted_items) == 1
    assert len(decrypted_items) == 1

    for name in encrypted_attributes:
        assert encrypted_items[0][name] != plaintext_item[name]
        assert decrypted_items[0][name] == plaintext_item[name]

    for name in unencrypted_attributes:
        assert decrypted_items[0][name] == encrypted_items[0][name] == plaintext_item[name]

    # shredding
    key_store.delete_key(key_id)

    encrypted = table.scan()
    decrypted = crypto_table.scan()

    assert encrypted["Count"] == 1
    assert len(encrypted["Items"]) == 1

    assert decrypted["Count"] == 0
    assert len(decrypted["Items"]) == 0
