from boto3.resources.base import ServiceResource

from ..key_store import KeyStore
from .object import CryptoObject


class CryptoBucket(object):
    def __init__(
        self,
        bucket: ServiceResource,
        key_store: KeyStore,
        nonce_size=12,
    ) -> None:
        self._bucket = bucket
        self._key_store = key_store
        self._nonce_size = nonce_size

    def put_object(self, key_id: str, Key, **kwargs):
        obj = CryptoObject(
            key_store=self._key_store,
            object=self._bucket.Object(Key),
            nonce_size=self._nonce_size,
        )
        return obj.put(key_id=key_id, **kwargs)

    def Object(self, key: str):
        return CryptoObject(
            key_store=self._key_store,
            object=self._bucket.Object(key),
            nonce_size=self._nonce_size,
        )

    def __getattr__(self, name):
        """Catch any method/attribute lookups that are not defined in this class and try
        to find them on the provided bridge object.
        :param str name: Attribute name
        :returns: Result of asking the provided bucket object for that attribute name
        :raises AttributeError: if attribute is not found on provided bridge object
        """
        return getattr(self._bucket, name)
