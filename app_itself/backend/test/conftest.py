import pytest
from fastapi.testclient import TestClient
import os
from unittest.mock import AsyncMock, patch
from pymongo import MongoClient

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from app import app

@pytest.fixture(scope="session")
def mongo_client():
    client = MongoClient(os.environ["MONGO_URI"])
    yield client
    client.close()

@pytest.fixture(autouse=True)
def clear_mongo(mongo_client):
    print("clearing mongo...")
    db = mongo_client["notesdb"]

    for collection_name in db.list_collection_names():
        db[collection_name].delete_many({})

        for doc in db[collection_name].find():
            print(doc)

    for collection_name in db.list_collection_names():
        db[collection_name].delete_many({})

        for doc in db[collection_name].find():
            print(doc)


@pytest.fixture
def client():
    return TestClient(app)
