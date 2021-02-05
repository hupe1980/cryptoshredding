import boto3
from botocore.client import BaseClient

from ..key_store import KeyStore
from .object import CryptoObject
from .stream_body_wrapper import StreamBodyWrapper


class CryptoS3(object):
    def __init__(
        self,
        client: BaseClient,
        key_store: KeyStore,
        nonce_size=12,
    ) -> None:
        self._client = client
        self._key_store = key_store
        self._nonce_size = nonce_size

    def put_object(self, key_id: str, Bucket: str, Key: str, **kwargs):
        obj = CryptoObject(
            key_store=self._key_store,
            object=boto3.resource('s3').Object(Bucket, Key),
            nonce_size=self._nonce_size,
        )
        return obj.put(key_id=key_id, **kwargs)

    def get_object(self, **kwargs):
        obj = self._client.get_object(**kwargs)

        obj["Body"] = StreamBodyWrapper(
            key_store=self._key_store,
            stream_body=obj["Body"],
            metadata=obj["Metadata"],
        )

        return obj

    def __getattr__(self, name):
        """Catch any method/attribute lookups that are not defined in this class and try
        to find them on the provided bridge object.
        :param str name: Attribute name
        :returns: Result of asking the provided client object for that attribute name
        :raises AttributeError: if attribute is not found on provided bridge object
        """
        return getattr(self._client, name)
