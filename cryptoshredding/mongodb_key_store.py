from pymongo.collection import Collection
from boto3.dynamodb.types import Binary
from dynamodb_encryption_sdk.material_providers import CryptographicMaterialsProvider

from .key_store import KeyStore


class MongodbKeyStore(KeyStore):
    def __init__(
        self,
        collection: Collection,
        materials_provider: CryptographicMaterialsProvider,
    ) -> None:
        super().__init__(
            table_name=collection.name,
            materials_provider=materials_provider,
        )
        self._collection = collection

    def _get_item(self, key_id: str):
        response = self._collection.find_one({"key_id": key_id})
        response["*amzn-ddb-map-desc*"] = Binary(response["*amzn-ddb-map-desc*"])
        response["*amzn-ddb-map-sig*"] = Binary(response["*amzn-ddb-map-sig*"])
        response["key"] = Binary(response["key"])
        del response["_id"]
        return response

    def _put_item(self, key_id: str, encrypted_item):
        encrypted_item["*amzn-ddb-map-desc*"] = bytes(encrypted_item["*amzn-ddb-map-desc*"].value)
        encrypted_item["*amzn-ddb-map-sig*"] = bytes(encrypted_item["*amzn-ddb-map-sig*"].value)
        encrypted_item["key"] = bytes(encrypted_item["key"].value)
        encrypted_item["_id"] = encrypted_item["key_id"]
        self._collection.insert_one(encrypted_item)

    def _delete_item(self, key_id: str):
        self._collection.delete_one({"key_id": key_id})
