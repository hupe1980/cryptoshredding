from . import create_in_memory_key_store


def test_key_generation():
    key_store = create_in_memory_key_store()
    new_key = key_store.create_key(key_id="foo")
    key = key_store.get_key(key_id="foo")

    assert key == new_key
