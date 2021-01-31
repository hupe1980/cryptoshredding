from .key_store import KeyStore
cache = {}


class InMemoryKeyStore(KeyStore):
    def _get_item(self, key_id: str):
        return cache[key_id]

    def _put_item(self, key_id: str, encrypted_item):
        cache[key_id] = encrypted_item

    def _delete_item(self, key_id: str):
        del cache[key_id]
