from dynamodb_encryption_sdk.encrypted.table import EncryptedTable
from dynamodb_encryption_sdk.structures import AttributeActions

from ..key_store import KeyStore
from .materials_provider import KeyStoreMaterialsProvider


class CryptoTable(object):
    def __init__(self, table, key_store: KeyStore,  attribute_actions=None):
        if attribute_actions is None:
            attribute_actions = AttributeActions()

        self._table = table
        self._key_store = key_store
        self._attribute_actions = attribute_actions

    def put_item(self, key_id: str, **kwargs):
        materials_provider = KeyStoreMaterialsProvider(
            key_store=self._key_store,
            material_description={"key_id": key_id},
        )
        encrypted_table = EncryptedTable(
            table=self._table,
            materials_provider=materials_provider,
            attribute_actions=self._attribute_actions,
        )
        encrypted_table.put_item(**kwargs)

    def get_item(self, **kwargs):
        materials_provider = KeyStoreMaterialsProvider(
            key_store=self._key_store,
        )
        encrypted_table = EncryptedTable(
            table=self._table,
            materials_provider=materials_provider,
            attribute_actions=self._attribute_actions,
        )
        return encrypted_table.get_item(**kwargs)
