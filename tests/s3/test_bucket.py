import boto3
import pytest
from moto import mock_s3

from cryptoshredding.s3 import CryptoBucket

from .. import create_in_memory_key_store


@pytest.fixture
def s3():
    with mock_s3():
        s3 = boto3.resource("s3", region_name="us-east-1")
        yield s3


@pytest.fixture
def bucket(s3):
    name = "dummy"
    s3.create_bucket(Bucket=name)
    return boto3.resource("s3").Bucket(name)


def test_put_object(bucket):
    key_id = "key"
    key_store = create_in_memory_key_store()
    key_store.create_key(key_id)

    crypto_bucket = CryptoBucket(
        bucket=bucket,
        key_store=key_store,
    )

    body = "foo bar"

    crypto_bucket.put_object(
        key_id=key_id,
        Key="object",
        Body=body,
    )

    obj = crypto_bucket.Object("object").get()

    assert body == obj["Body"].read().decode("utf8")
