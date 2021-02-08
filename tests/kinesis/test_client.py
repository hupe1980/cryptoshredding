import boto3
import pytest
from moto import mock_kinesis

from cryptoshredding.kinesis import CryptoClient

from .. import create_in_memory_key_store


@pytest.fixture
def kinesis():
    with mock_kinesis():
        kinesis = boto3.client("kinesis", region_name="us-east-1")
        yield kinesis


def test_get_object(kinesis):
    key_id = "key"
    key_store = create_in_memory_key_store()
    key_store.create_main_key(key_id)

    stream_name = "dummy"
    kinesis.create_stream(
        StreamName=stream_name,
        ShardCount=1,
    )

    crypto_kinesis = CryptoClient(
        client=kinesis,
        key_store=key_store,
    )

    data = b"foo bar"

    crypto_kinesis.put_record(
        CSEKeyId=key_id,
        StreamName=stream_name,
        Data=data,
        PartitionKey="key1",
    )

    response = crypto_kinesis.describe_stream(
        StreamName=stream_name,
    )
    shard_id = response["StreamDescription"]["Shards"][0]["ShardId"]

    response = crypto_kinesis.get_shard_iterator(
        StreamName=stream_name,
        ShardId=shard_id,
        ShardIteratorType="TRIM_HORIZON",
    )
    shard_iterator = response["ShardIterator"]

    encrypred_response = kinesis.get_records(ShardIterator=shard_iterator)
    decrypred_response = crypto_kinesis.get_records(ShardIterator=shard_iterator)

    assert len(encrypred_response["Records"]) == 1
    assert data != encrypred_response["Records"][0]["Data"]

    assert len(decrypred_response["Records"]) == 1
    assert data == decrypred_response["Records"][0]["Data"]
