import base64
import json
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .stream_body_wrapper import StreamBodyWrapper


class CryptoObject(object):
    def __init__(self, key_store, object, nonce_size=12,) -> None:
        self._key_store = key_store
        self._object = object
        self._nonce_size = nonce_size

    def put(self, key_id: str, Body, **kwargs):
        key = self._key_store.get_key(key_id)
        aesgcm = AESGCM(key)
        encryption_context = {"key_id": key_id}
        iv = os.urandom(self._nonce_size)
        encrypted_body = aesgcm.encrypt(iv, Body.encode(), None)

        metadata = kwargs.pop('Metadata', {})
        metadata['x-amz-matdesc'] = json.dumps(encryption_context)
        metadata['x-amz-iv'] = base64.b64encode(iv).decode()
        metadata['x-amz-cek-alg'] = 'AES/GCM/NoPadding'

        return self._object.put(
            Body=encrypted_body,
            Metadata=metadata,
            **kwargs
        )

    def get(self):
        obj = self._object.get()

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
        :returns: Result of asking the provided object object for that attribute name
        :raises AttributeError: if attribute is not found on provided bridge object
        """
        return getattr(self._object, name)
