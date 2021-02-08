import base64
import hashlib
import json
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from ..key_store import KeyStore
from .stream_body_wrapper import StreamBodyWrapper


class CryptoObject(object):
    def __init__(
        self,
        key_store: KeyStore,
        object,
    ) -> None:
        self._key_store = key_store
        self._object = object

    def put(self, CSEKeyId: str, Body, **kwargs):
        main_key = self._key_store.get_main_key(CSEKeyId)
        data_key, encrypted_data_key = main_key.generate_data_key()

        encryption_context = {"key_id": CSEKeyId}
        iv = os.urandom(12)
        md5 = base64.b64encode(hashlib.md5(Body.encode()).digest())
        content_length = str(len(Body))

        encrypted_body = AESGCM(data_key).encrypt(iv, Body.encode(), None)

        metadata = kwargs.pop("Metadata", {})
        # Unencrypted content length.
        metadata["x-amz-unencrypted-content-length"] = content_length
        # Unencrypted content hash.
        metadata["x-amz-unencrypted-content-md5"] = md5.decode()
        # Tag length (in bits) when AEAD is in use.
        metadata["x-amz-tag-len"] = str(128)
        # Key wrapping algorithm used.
        metadata["x-amz-wrap-alg"] = "AESWrap"
        # Customer provided material description in JSON format.
        metadata["x-amz-matdesc"] = json.dumps(encryption_context)
        # Randomly generated IV(per S3 object), base64 encoded.
        metadata["x-amz-iv"] = base64.b64encode(iv).decode()
        # Content encryption algorithm used.
        metadata["x-amz-cek-alg"] = "AES/GCM/NoPadding"
        # CEK in key wrapped form.
        metadata["x-amz-key-v2"] = base64.b64encode(encrypted_data_key).decode()

        return self._object.put(Body=base64.b64encode(encrypted_body).decode(), Metadata=metadata, **kwargs)

    def get(self):
        obj = self._object.get()

        obj["Body"] = StreamBodyWrapper(
            key_store=self._key_store,
            stream_body=obj["Body"],
            metadata=obj["Metadata"],
        )
        return obj

    def __getattr__(self, name: str):
        """Catch any method/attribute lookups that are not defined in this class and try
        to find them on the provided bridge object.
        :param str name: Attribute name
        :returns: Result of asking the provided object object for that attribute name
        :raises AttributeError: if attribute is not found on provided bridge object
        """
        return getattr(self._object, name)
