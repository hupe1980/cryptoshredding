from typing import Optional
from boto3.resources.base import ServiceResource
from dynamodb_encryption_sdk.structures import AttributeActions

from ..key_store import KeyStore
from .cache import TableInfoCache
from .table import CryptoTable


class CryptoResource(object):
    def __init__(
        self,
        resource: ServiceResource,
        key_store: KeyStore,
        attribute_actions: Optional[AttributeActions] = None,
        auto_refresh_table_indexes: bool = True,
    ) -> None:
        if attribute_actions is None:
            attribute_actions = AttributeActions()

        self._resource = resource
        self._key_store = key_store
        self._attribute_actions = attribute_actions
        self._auto_refresh_table_indexes = auto_refresh_table_indexes
        self._table_info_cache = TableInfoCache(
            client=self._resource.meta.client,
            auto_refresh_table_indexes=self._auto_refresh_table_indexes,
        )

    def Table(self, name: str, **kwargs) -> CryptoTable:
        """Creates an CryptoTable resource."""
        return CryptoTable(
            table=self._resource.Table(name),
            key_store=self._key_store,
            attribute_actions=kwargs.get("attribute_actions", self._attribute_actions),
            auto_refresh_table_indexes=kwargs.get("auto_refresh_table_indexes", self._auto_refresh_table_indexes),
            table_info=self._table_info_cache.table_info(name),
        )

    def __getattr__(self, name):
        """Catch any method/attribute lookups that are not defined in this class and try
        to find them on the provided resource object.
        :param str name: Attribute name
        :returns: Result of asking the provided resource object for that attribute name
        :raises AttributeError: if attribute is not found on provided resource object
        """
        return getattr(self._resource, name)
