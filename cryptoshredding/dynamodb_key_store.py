from .key_store import KeyStore


class DynamodbKeyStore(KeyStore):
    def __init__(self, table, materials_provider):
        super().__init__(table_name=table.table_name, materials_provider=materials_provider)
        self._table = table

    def _get_item(self, key_id: str):
        response = self._table.get_item(Key={"key_id": key_id})
        return response["Item"]

    def _put_item(self, key_id: str, encrypted_item):
        self._table.put_item(Item=encrypted_item)

    def _delete_item(self, key_id: str):
        self._table_delete_item(Key={"key_id": key_id})
