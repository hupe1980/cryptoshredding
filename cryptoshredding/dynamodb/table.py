from typing import Optional
from boto3.resources.base import ServiceResource
from dynamodb_encryption_sdk.structures import (
    AttributeActions,
    TableInfo,
    EncryptionContext,
)
from dynamodb_encryption_sdk.encrypted.table import EncryptedTable


from ..key_store import KeyStore
from .item import decrypt_python_item
from .materials_provider import KeyStoreMaterialsProvider


class CryptoTable(object):
    """High-level helper class to provide a boto3 familiar interface to encrypted tables."""

    def __init__(
        self,
        table: ServiceResource,
        key_store: KeyStore,
        table_info: Optional[TableInfo] = None,
        attribute_actions: Optional[AttributeActions] = None,
        auto_refresh_table_indexes: Optional[bool] = True,
    ) -> None:
        if attribute_actions is None:
            attribute_actions = AttributeActions()

        if table_info is None:
            table_info = TableInfo(name=table.name)

        if auto_refresh_table_indexes:
            table_info.refresh_indexed_attributes(table.meta.client)

        self._table = table
        self._key_store = key_store
        self._table_info = table_info
        self._attribute_actions = attribute_actions

    def put_item(self, CSEKeyId: str, **kwargs):
        materials_provider = KeyStoreMaterialsProvider(
            key_store=self._key_store,
            material_description={"key_id": CSEKeyId},
        )
        encrypted_table = EncryptedTable(
            table=self._table,
            materials_provider=materials_provider,
            table_info=self._table_info,
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
            table_info=self._table_info,
            attribute_actions=self._attribute_actions,
        )
        return encrypted_table.get_item(**kwargs)

    def query(self, **kwargs):
        response = self._table.query(**kwargs)
        return self._decrypt_dynamodb_response(response)

    def scan(self, **kwargs):
        response = self._table.scan(**kwargs)
        return self._decrypt_dynamodb_response(response)

    def update_item(self, **kwargs):
        """Update item is not yet supported."""
        raise NotImplementedError('"update_item" is not yet implemented')

    def _decrypt_dynamodb_response(self, response):
        ec_kwargs = self._table_info.encryption_context_values
        if self._table_info.primary_index is not None:
            ec_kwargs.update(
                {
                    "partition_key_name": self._table_info.primary_index.partition,
                    "sort_key_name": self._table_info.primary_index.sort,
                }
            )

        self._attribute_actions.set_index_keys(*self._table_info.protected_index_keys())

        encryption_context = EncryptionContext(**ec_kwargs)

        def decrypt(items):
            for item in items:
                try:
                    decrypted_item = decrypt_python_item(
                        item=item,
                        key_store=self._key_store,
                        encryption_context=encryption_context,
                        attribute_actions=self._attribute_actions,
                    )
                    yield decrypted_item
                except Exception:  # TODO
                    pass

        response["Items"] = list(decrypt(response["Items"]))
        response["Count"] = len(response["Items"])

        return response

    def __getattr__(self, name):
        """Catch any method/attribute lookups that are not defined in this class and try
        to find them on the provided bridge object.
        :param str name: Attribute name
        :returns: Result of asking the provided table object for that attribute name
        :raises AttributeError: if attribute is not found on provided bridge object
        """
        return getattr(self._table, name)
