import codecs
import aws_encryption_sdk
from aws_encryption_sdk import CommitmentPolicy
# from aws_encryption_sdk.structures import MessageHeader

from ..key_store import KeyStore
from .key_provider import KeyStoreMasterKeyProvider


class CryptoString(object):
    def __init__(
        self,
        key_store: KeyStore,
        commitment_policy: CommitmentPolicy = CommitmentPolicy.REQUIRE_ENCRYPT_REQUIRE_DECRYPT
    ) -> None:
        self._key_store = key_store
        self._client = aws_encryption_sdk.EncryptionSDKClient(
            commitment_policy=commitment_policy,
        )

    def encrypt(self, key_id: str, source: str):  # -> tuple[bytes, MessageHeader]:
        kwargs = dict(
            key_store=self._key_store,
        )
        key_provider = KeyStoreMasterKeyProvider(**kwargs)
        key_provider.add_master_key(key_id)

        ciphertext, encryptor_header = self._client.encrypt(
            source=source,
            key_provider=key_provider,
        )

        return ciphertext, encryptor_header

    def decrypt(self, source: bytes):  # -> tuple[str, MessageHeader]:
        kwargs = dict(
            key_store=self._key_store,
        )
        key_provider = KeyStoreMasterKeyProvider(**kwargs)

        plaintext, encryptor_header = self._client.decrypt(
            source=source,
            key_provider=key_provider,
        )

        return codecs.decode(plaintext, "utf8"), encryptor_header
