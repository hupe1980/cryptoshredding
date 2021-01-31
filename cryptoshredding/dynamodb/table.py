from dynamodb_encryption_sdk.delegated_keys.jce import JceNameLocalDelegatedKey
from dynamodb_encryption_sdk.encrypted.table import EncryptedTable
from dynamodb_encryption_sdk.material_providers.wrapped import WrappedCryptographicMaterialsProvider
from dynamodb_encryption_sdk.identifiers import EncryptionKeyType, KeyEncodingType
from dynamodb_encryption_sdk.structures import AttributeActions

from ..key_store import KeyStore


class CryptoTable(object):
    def __init__(self, table, key_store: KeyStore,  attribute_actions=None):
        if attribute_actions is None:
            attribute_actions = AttributeActions()

        self._table = table
        self._key_store = key_store
        self._attribute_actions = attribute_actions

    def put_item(self, key_id: str, **kwargs):
        materials_provider = self._create_materials_provider(key_id=key_id)
        encrypted_table = EncryptedTable(
            table=self._table,
            materials_provider=materials_provider,
            attribute_actions=self._attribute_actions,
        )
        encrypted_table.put_item(**kwargs)

    def get_item(self, key_id: str, **kwargs):
        materials_provider = self._create_materials_provider(key_id=key_id)
        encrypted_table = EncryptedTable(
            table=self._table,
            materials_provider=materials_provider,
            attribute_actions=self._attribute_actions,
        )
        return encrypted_table.get_item(**kwargs)

    def _create_materials_provider(self, key_id: str):
        key_bytes = self._key_store.get_key(key_id=key_id)

        wrapping_key = JceNameLocalDelegatedKey(
            key=key_bytes,
            algorithm="AES",
            key_type=EncryptionKeyType.SYMMETRIC,
            key_encoding=KeyEncodingType.RAW,
        )
        signing_key = JceNameLocalDelegatedKey(
            key=key_bytes,
            algorithm="HmacSHA512",
            key_type=EncryptionKeyType.SYMMETRIC,
            key_encoding=KeyEncodingType.RAW,
        )
        wrapped_cmp = WrappedCryptographicMaterialsProvider(
            wrapping_key=wrapping_key,
            unwrapping_key=wrapping_key,
            signing_key=signing_key,
        )

        return wrapped_cmp
