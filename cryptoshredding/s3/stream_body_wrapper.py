import base64
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from ..key_store import KeyStore


class StreamBodyWrapper(object):
    def __init__(self, key_store: KeyStore, stream_body, metadata) -> None:
        self._key_store = key_store
        self._stream_body = stream_body
        self._metadata = metadata

    def read(self):
        iv = base64.b64decode(self._metadata["x-amz-iv"])
        encrypted_data_key = base64.b64decode(self._metadata["x-amz-key-v2"])
        encryption_context = json.loads(self._metadata["x-amz-matdesc"])
        main_key = self._key_store.get_main_key(encryption_context["key_id"])
        data_key = main_key.decrypt(encrypted_data_key)
        bytes = base64.b64decode(self._stream_body.read())

        return AESGCM(data_key).decrypt(iv, bytes, None)

    def __getattr__(self, name: str):
        """Catch any method/attribute lookups that are not defined in this class and try
        to find them on the provided bridge object.
        :param str name: Attribute name
        :returns: Result of asking the provided stream object for that attribute name
        :raises AttributeError: if attribute is not found on provided bridge object
        """
        return getattr(self._stream_body, name)
