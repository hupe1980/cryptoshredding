from botocore.client import BaseClient
from dynamodb_encryption_sdk.structures import TableInfo


class TableInfoCache(object):
    def __init__(
        self,
        client: BaseClient,
        auto_refresh_table_indexes: bool,
    ) -> None:
        self._client = client
        self._auto_refresh_table_indexes = auto_refresh_table_indexes
        self._table_infos = {}

    def table_info(self, table_name: str):
        try:
            return self._table_infos[table_name]
        except KeyError:
            _table_info = TableInfo(name=table_name)
            if self._auto_refresh_table_indexes:
                _table_info.refresh_indexed_attributes(self._client)
            self._table_infos[table_name] = _table_info
            return _table_info
