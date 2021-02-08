from boto3.resources.base import ServiceResource


class CryptoResource(object):
    def __init__(
        self,
        resource: ServiceResource,
        key_store,
        attribute_actions=None,
        auto_refresh_table_indexes=True,
    ) -> None:
        pass

    def Table(self, name, **kwargs):
        pass

    def __getattr__(self, name):
        """Catch any method/attribute lookups that are not defined in this class and try
        to find them on the provided resource object.
        :param str name: Attribute name
        :returns: Result of asking the provided resource object for that attribute name
        :raises AttributeError: if attribute is not found on provided resource object
        """
        return getattr(self._resource, name)
