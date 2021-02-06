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


def test_object_get(bucket):
    key_id = "key"
    key_store = create_in_memory_key_store()
    key_store.create_main_key(key_id)

    crypto_bucket = CryptoBucket(
        bucket=bucket,
        key_store=key_store,
    )

    body = "foo bar 4711"

    crypto_bucket.put_object(
        CSEKeyId=key_id,
        Key="object",
        Body=body,
    )

    encrypted_obj = bucket.Object("object").get()
    decrypted_obj = crypto_bucket.Object("object").get()

    assert body != encrypted_obj["Body"].read().decode("utf8")
    assert body == decrypted_obj["Body"].read().decode("utf8")


def test_data_key(bucket):
    key_id = "key"
    key_store = create_in_memory_key_store()
    key_store.create_main_key(key_id)

    crypto_bucket = CryptoBucket(
        bucket=bucket,
        key_store=key_store,
    )

    body = "foo bar 4711"

    crypto_bucket.put_object(
        CSEKeyId=key_id,
        Key="object1",
        Body=body,
    )

    crypto_bucket.put_object(
        CSEKeyId=key_id,
        Key="object2",
        Body=body,
    )

    decrypted_obj1 = crypto_bucket.Object("object1").get()
    decrypted_obj2 = crypto_bucket.Object("object2").get()

    assert decrypted_obj1["Metadata"]["x-amz-key-v2"] != decrypted_obj2["Metadata"]["x-amz-key-v2"]
    assert decrypted_obj1["Metadata"]["x-amz-iv"] != decrypted_obj2["Metadata"]["x-amz-iv"]
