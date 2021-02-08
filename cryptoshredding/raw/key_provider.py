import codecs
from aws_encryption_sdk.key_providers.base import (
    MasterKey,
    MasterKeyConfig,
    MasterKeyProvider,
    MasterKeyProviderConfig,
)
from aws_encryption_sdk.structures import (
    DataKey,
    EncryptedDataKey,
    MasterKeyInfo,
)

from ..key_store import KeyStore
from ..main_key import MainKey


_PROVIDER_ID = "key_store"


class KeyStoreMasterKeyProviderConfig(MasterKeyProviderConfig):
    def __init__(self, **kwargs):
        self._key_store = kwargs.get("key_store")

    @property
    def key_store(self):
        return self._key_store


class KeyStoreMasterKeyProvider(MasterKeyProvider):
    provider_id = _PROVIDER_ID
    _config_class = KeyStoreMasterKeyProviderConfig

    def __init__(self, **kwargs):
        self._key_store: KeyStore = self.config.key_store

    def _new_master_key(self, key_id: bytes):
        main_key = self._key_store.get_main_key(codecs.decode(key_id, "utf8"))
        return KeyStoreMasterKey(config=KeyStoreMasterKeyConfig(key_id=key_id, main_key=main_key))


class KeyStoreMasterKeyConfig(MasterKeyConfig):
    provider_id = _PROVIDER_ID

    def __init__(self, **kwargs):
        self._main_key = kwargs.get("main_key")
        self.key_id = kwargs.get("key_id")


class KeyStoreMasterKey(MasterKey):
    provider_id = _PROVIDER_ID
    _config_class = KeyStoreMasterKeyConfig

    def __init__(self, **kwargs):
        self._main_key: MainKey = self.config._main_key

    def _generate_data_key(self, algorithm, encryption_context=None):
        data_key, encrypted_data_key = self._main_key.generate_data_key()
        return DataKey(
            key_provider=MasterKeyInfo(
                provider_id=self.provider_id,
                key_info=self._main_key.key_id,
            ),
            data_key=data_key,
            encrypted_data_key=encrypted_data_key,
        )

    def _encrypt_data_key(self, data_key, algorithm, encryption_context=None):
        encrypted_data_key = self._main_key.encrypt(data_key.data_key)
        return EncryptedDataKey(
            key_provider=MasterKeyInfo(
                provider_id=self.provider_id,
                key_info=self._main_key.key_id,
            ),
            encrypted_data_key=encrypted_data_key,
        )

    def _decrypt_data_key(self, encrypted_data_key, algorithm, encryption_context=None):
        data_key = self._main_key.decrypt(encrypted_data_key.encrypted_data_key)
        return DataKey(
            key_provider=MasterKeyInfo(
                provider_id=self.provider_id,
                key_info=self._main_key.key_id,
            ),
            data_key=data_key,
            encrypted_data_key=encrypted_data_key.encrypted_data_key,
        )
