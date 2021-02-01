from abc import ABC, abstractmethod
import os

from dynamodb_encryption_sdk.identifiers import CryptoAction
from dynamodb_encryption_sdk.structures import AttributeActions, EncryptionContext
from dynamodb_encryption_sdk.encrypted import CryptoConfig
from dynamodb_encryption_sdk.encrypted.item import decrypt_python_item, encrypt_python_item
from dynamodb_encryption_sdk.transform import dict_to_ddb


def key_generator() -> bytes:
    return os.urandom(32)


class KeyStore(ABC):
    @abstractmethod
    def _get_item(self, key_id: str):
        pass

    @abstractmethod
    def _put_item(self, key_id: str, encrypted_item):
        pass

    @abstractmethod
    def _delete_item(self, key_id: str) -> None:
        pass

    def __init__(self, materials_provider, table_name="key_store_table", key_generator=key_generator):
        self._materials_provider = materials_provider
        self._table_name = table_name
        self._key_generator = key_generator
        self._actions = AttributeActions(
            default_action=CryptoAction.ENCRYPT_AND_SIGN, attribute_actions={
                "restricted": CryptoAction.DO_NOTHING,
                "on_hold": CryptoAction.DO_NOTHING,
                "ttl": CryptoAction.DO_NOTHING,
            }
        )
        self._actions.set_index_keys("key_id")

    def create_key(self, key_id: str) -> bytes:
        index_key = {"key_id": key_id}
        key = self._key_generator()
        plaintext_item = {
            "restricted": False,
            "on_hold": False,
            "key": key,
        }
        plaintext_item.update(index_key)

        encryption_context = EncryptionContext(
            table_name=self._table_name,
            partition_key_name="key_id",
            attributes=dict_to_ddb(index_key),
        )
        crypto_config = CryptoConfig(
            materials_provider=self._materials_provider,
            encryption_context=encryption_context,
            attribute_actions=self._actions
        )
        encrypted_item = encrypt_python_item(plaintext_item, crypto_config)

        self._put_item(key_id=key_id, encrypted_item=encrypted_item)

        return key

    def get_key(self, key_id: str) -> bytes:
        index_key = {"key_id": key_id}

        encryption_context = EncryptionContext(
            table_name=self._table_name,
            partition_key_name="key_id",
            attributes=dict_to_ddb(index_key),
        )
        crypto_config = CryptoConfig(
            materials_provider=self._materials_provider,
            encryption_context=encryption_context,
            attribute_actions=self._actions,
        )

        encrypted_item = self._get_item(key_id=key_id)

        if encrypted_item["restricted"]:
            raise Exception("Access restricted.")

        decrypted_item = decrypt_python_item(encrypted_item, crypto_config)

        return decrypted_item["key"].value

    def delete_key(self, key_id: str, allow_recovering=False) -> None:
        encrypted_item = self._get_item(key_id=key_id)

        if encrypted_item["on_hold"]:
            raise Exception("Deletion currently not possible.")

        self._delete_item(key_id=key_id)
