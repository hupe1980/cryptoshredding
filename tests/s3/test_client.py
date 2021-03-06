import boto3
import pytest
from moto import mock_s3

from cryptoshredding.s3 import CryptoS3

from .. import create_in_memory_key_store


@pytest.fixture
def s3():
    with mock_s3():
        s3 = boto3.client("s3", region_name="us-east-1")
        yield s3


@pytest.fixture
def bucket(s3):
    name = "dummy"
    s3.create_bucket(Bucket=name)
    return boto3.resource("s3").Bucket(name)


def test_get_object(s3, bucket):
    key_id = "key"
    key_store = create_in_memory_key_store()
    key_store.create_main_key(key_id)

    crypto_s3 = CryptoS3(
        client=s3,
        key_store=key_store,
    )

    body = "foo bar"

    crypto_s3.put_object(
        CSEKeyId=key_id,
        Bucket=bucket.name,
        Key="object",
        Body=body,
    )

    encrypted_obj = s3.get_object(
        Bucket=bucket.name,
        Key="object",
    )

    decrypted_obj = crypto_s3.get_object(
        Bucket=bucket.name,
        Key="object",
    )

    assert body != encrypted_obj["Body"].read().decode("utf8")
    assert body == decrypted_obj["Body"].read().decode("utf8")
