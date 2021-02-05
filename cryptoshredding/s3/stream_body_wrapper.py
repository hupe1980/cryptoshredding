import base64
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class StreamBodyWrapper(object):
    def __init__(self, key_store, stream_body, metadata):
        self._key_store = key_store
        self._stream_body = stream_body
        self._metadata = metadata

    def read(self):
        iv = base64.b64decode(self._metadata['x-amz-iv'])
        encryption_context = json.loads(self._metadata['x-amz-matdesc'])
        key = self._key_store.get_key(encryption_context["key_id"])
        aesgcm = AESGCM(key)

        bytes = self._stream_body.read()

        return aesgcm.decrypt(iv, bytes, None)

    def __getattr__(self, name):
        return getattr(self._stream_body, name)
