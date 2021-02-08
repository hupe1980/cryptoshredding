from aws_encryption_sdk import EncryptionSDKClient, CommitmentPolicy

# from aws_encryption_sdk.structures import MessageHeader

from ..key_store import KeyStore
from .key_provider import KeyStoreMasterKeyProvider


class CryptoBytes(object):
    def __init__(
        self,
        key_store: KeyStore,
        commitment_policy: CommitmentPolicy = CommitmentPolicy.REQUIRE_ENCRYPT_REQUIRE_DECRYPT,
    ) -> None:
        self._key_store = key_store
        self._client = EncryptionSDKClient(
            commitment_policy=commitment_policy,
        )

    def encrypt(self, key_id: str, data: bytes):  # -> tuple[bytes, MessageHeader]:
        kwargs = dict(
            key_store=self._key_store,
        )
        key_provider = KeyStoreMasterKeyProvider(**kwargs)
        key_provider.add_master_key(key_id)

        encrypted, header = self._client.encrypt(
            source=data,
            key_provider=key_provider,
        )

        return encrypted, header

    def decrypt(self, data: bytes):  # -> tuple[bytes, MessageHeader]:
        kwargs = dict(
            key_store=self._key_store,
        )
        key_provider = KeyStoreMasterKeyProvider(**kwargs)

        plain, header = self._client.decrypt(
            source=data,
            key_provider=key_provider,
        )

        return plain, header
