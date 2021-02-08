from typing import Optional
from botocore.client import BaseClient
from dynamodb_encryption_sdk.structures import AttributeActions

from ..key_store import KeyStore


class CryptoClient(object):
    def __init__(
        self,
        client: BaseClient,
        key_store: KeyStore,
        attribute_actions: Optional[AttributeActions] = None,
        auto_refresh_table_indexes: bool = True,
        expect_standard_dictionaries: bool = False,
    ) -> None:
        if attribute_actions is None:
            attribute_actions = AttributeActions()

        self._client = client
        self._key_store = key_store
        self._attribute_actions = attribute_actions
        self._auto_refresh_table_indexes = auto_refresh_table_indexes
        self._expect_standard_dictionaries = expect_standard_dictionaries

    def update_item(self, **kwargs):
        """Update item is not yet supported.
        :raises NotImplementedError: if called
        """
        raise NotImplementedError('"update_item" is not yet implemented')

    def __getattr__(self, name):
        """Catch any method/attribute lookups that are not defined in this class and try
        to find them on the provided client object.
        :param str name: Attribute name
        :returns: Result of asking the provided client object for that attribute name
        :raises AttributeError: if attribute is not found on provided client object
        """
        return getattr(self._client, name)
