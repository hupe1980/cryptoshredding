import aws_encryption_sdk
from aws_encryption_sdk import CommitmentPolicy

from ..key_store import KeyStore
from .key_provider import KeyStoreMasterKeyProvider


class CryptoFile(object):
    def __init__(
        self,
        key_store: KeyStore,
        commitment_policy: CommitmentPolicy = CommitmentPolicy.REQUIRE_ENCRYPT_REQUIRE_DECRYPT,
    ) -> None:
        self._key_store = key_store
        self._client = aws_encryption_sdk.EncryptionSDKClient(
            commitment_policy=commitment_policy,
        )

    def encrypt(self, key_id: str, plaintext_filename: str, ciphertext_filename: str) -> None:
        kwargs = dict(
            key_store=self._key_store,
        )
        key_provider = KeyStoreMasterKeyProvider(**kwargs)
        key_provider.add_master_key(key_id)

        with open(plaintext_filename, "rb") as plaintext, open(ciphertext_filename, "wb") as ciphertext:
            with self._client.stream(mode="e", source=plaintext, key_provider=key_provider) as encryptor:
                for chunk in encryptor:
                    ciphertext.write(chunk)

    def decrypt(self, ciphertext_filename: str, plaintext_filename: str) -> None:
        kwargs = dict(
            key_store=self._key_store,
        )
        key_provider = KeyStoreMasterKeyProvider(**kwargs)

        with open(ciphertext_filename, "rb") as ciphertext, open(plaintext_filename, "wb") as plaintext:
            with self._client.stream(mode="d", source=ciphertext, key_provider=key_provider) as decryptor:
                for chunk in decryptor:
                    plaintext.write(chunk)
