from boto3.resources.base import ServiceResource

from ..key_store import KeyStore
from .object import CryptoObject


class CryptoBucket(object):
    def __init__(
        self,
        bucket: ServiceResource,
        key_store: KeyStore,
    ) -> None:
        self._bucket = bucket
        self._key_store = key_store

    def put_object(self, CSEKeyId: str, Key: str, **kwargs):
        obj = CryptoObject(
            key_store=self._key_store,
            object=self._bucket.Object(Key),
        )
        return obj.put(CSEKeyId=CSEKeyId, **kwargs)

    def Object(self, key: str) -> CryptoObject:
        return CryptoObject(
            key_store=self._key_store,
            object=self._bucket.Object(key),
        )

    def __getattr__(self, name: str):
        """Catch any method/attribute lookups that are not defined in this class and try
        to find them on the provided bridge object.
        :param str name: Attribute name
        :returns: Result of asking the provided bucket object for that attribute name
        :raises AttributeError: if attribute is not found on provided bridge object
        """
        return getattr(self._bucket, name)
