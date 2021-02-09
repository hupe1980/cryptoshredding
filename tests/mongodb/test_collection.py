import pytest
import mongomock


@pytest.fixture
def client():
    client = mongomock.MongoClient()
    yield client
    client.close()


def test_find_one(client):
    collection = client.db.users
    print(collection)
    objects = [dict(votes=1), dict(votes=2)]
    collection.insert_many(objects)
    print(collection)
    result = collection.find()
    for doc in result:
        print(doc)
