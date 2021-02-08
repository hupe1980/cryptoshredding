import botocore


class CryptoClient(object):
    def __init__(
        self,
        client: botocore.client.BaseClient,
        key_store,
        attribute_actions=None,
        auto_refresh_table_indexes=True,
        expect_standard_dictionaries=False,
    ) -> None:
        pass

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
