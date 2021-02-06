import boto3
import pytest
from moto import mock_s3

from cryptoshredding.s3 import CryptoObject

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


def test_get(bucket):
    key_id = "key"
    key_store = create_in_memory_key_store()
    key_store.create_main_key(key_id)

    object = bucket.Object("object")

    crypto_object = CryptoObject(
        object=object,
        key_store=key_store,
    )

    body = "foo bar 4711"

    crypto_object.put(
        CSEKeyId=key_id,
        Body=body,
    )

    encrypted_obj = object.get()
    decrypted_obj = crypto_object.get()

    assert body != encrypted_obj["Body"].read().decode("utf8")
    assert body == decrypted_obj["Body"].read().decode("utf8")
