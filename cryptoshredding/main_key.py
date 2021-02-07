import os
from cryptography.hazmat.primitives.keywrap import aes_key_wrap, aes_key_unwrap


class MainKey(object):
    def __init__(self, key_id: str, key_bytes: bytes):
        self._key_id = key_id
        self._key_bytes = key_bytes

    def generate_data_key(self):  # -> tuple[bytes, bytes]:
        data_key = os.urandom(32)
        encrypted_data_key = aes_key_wrap(
            wrapping_key=self._key_bytes,
            key_to_wrap=data_key,
        )
        return data_key, encrypted_data_key

    def encrypt(self, data_key: bytes) -> bytes:
        encrypted_data_key = aes_key_wrap(
            wrapping_key=self._key_bytes,
            key_to_wrap=data_key,
        )
        return encrypted_data_key

    def decrypt(self, encrypted_data_key) -> bytes:
        data_key = aes_key_unwrap(
            wrapping_key=self._key_bytes,
            wrapped_key=encrypted_data_key,
        )
        return data_key

    @property
    def key_id(self):
        return self._key_id

    @property
    def key_bytes(self):
        return self._key_bytes
