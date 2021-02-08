from . import create_in_memory_key_store


def test_key_generation():
    key_store = create_in_memory_key_store()

    key_id = "key1"
    new_main_key = key_store.create_main_key(key_id)
    main_key = key_store.get_main_key(key_id)

    assert main_key.key_id == new_main_key.key_id
    assert main_key.key_bytes == new_main_key.key_bytes
