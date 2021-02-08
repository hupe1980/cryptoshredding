from botocore.client import BaseClient

from ..key_store import KeyStore
from ..raw import CryptoBytes


class CryptoClient(object):
    def __init__(
        self,
        client: BaseClient,
        key_store: KeyStore,
    ) -> None:
        self._client = client
        self._crypto_bytes = CryptoBytes(
            key_store=key_store,
        )

    def put_record(self, CSEKeyId: str, Data: bytes, **kwargs):
        """Writes a single encrypted data record into an Amazon Kinesis data stream."""
        encrypted_data, _header = self._crypto_bytes.encrypt(
            key_id=CSEKeyId,
            data=Data,
        )
        return self._client.put_record(
            Data=encrypted_data,
            **kwargs,
        )

    def get_records(self, **kwargs):
        response = self._client.get_records(**kwargs)
        return self._decrypt_kinesis_response(response)

    def _decrypt_kinesis_response(self, response):
        def decrypt(records):
            for record in records:
                try:
                    decrypted_data, _header = self._crypto_bytes.decrypt(data=record["Data"])
                    record["Data"] = decrypted_data
                    yield record
                except Exception:  # TODO
                    pass

        response["Records"] = list(decrypt(response["Records"]))
        return response

    def __getattr__(self, name):
        """Catch any method/attribute lookups that are not defined in this class and try
        to find them on the provided client object.
        :param str name: Attribute name
        :returns: Result of asking the provided client object for that attribute name
        :raises AttributeError: if attribute is not found on provided client object
        """
        return getattr(self._client, name)
