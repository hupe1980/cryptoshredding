from botocore.client import BaseClient
from botocore.exceptions import ClientError
from boto3.resources.base import ServiceResource
from dynamodb_encryption_sdk.material_providers import CryptographicMaterialsProvider

from .key_store import KeyStore


class DynamodbKeyStore(KeyStore):
    def __init__(
        self,
        table: ServiceResource,
        materials_provider: CryptographicMaterialsProvider,
    ) -> None:
        super().__init__(
            table_name=table.table_name,
            materials_provider=materials_provider,
        )
        self._table = table

    @classmethod
    def create_table(cls, client: BaseClient, table_name: str) -> None:
        """Create the table for this KeyStore."""
        try:
            client.create_table(
                TableName=table_name,
                KeySchema=[
                    {"AttributeName": "key_id", "KeyType": "HASH"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": "key_id", "AttributeType": "S"},
                ],
                BillingMode="PAY_PER_REQUEST",
            )
        except ClientError as exc:
            raise Exception("Could not create table", exc)

    def _get_item(self, key_id: str):
        response = self._table.get_item(Key={"key_id": key_id})
        return response["Item"]

    def _put_item(self, key_id: str, encrypted_item):
        self._table.put_item(Item=encrypted_item)

    def _delete_item(self, key_id: str):
        self._table_delete_item(Key={"key_id": key_id})
