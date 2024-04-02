import pytest
from unittest.mock import MagicMock
from typing import Any
from pymongo.cursor import Cursor
from infrastructure.data.storage.mongodb.mongodb_data_storage import MongoDBDataStorage


@pytest.fixture
def data() -> dict[str, Any]:
    return {"time": 1711644891, "value": [68, 51, 127, 191], "tags": []}


@pytest.fixture
def invalidation_reasons() -> dict[str, Any]:
    return {"time": 1711644891, "reasons": ["fake_reason"]}


@pytest.fixture
def mongodb_data_storage_client() -> MongoDBDataStorage:
    mongodb_client = MongoDBDataStorage()
    mongodb_client.data_collection = MagicMock()
    mongodb_client.discard_collection = MagicMock()
    return mongodb_client


class TestMongoDBDataStorage:
    @staticmethod
    def test_save_data(mongodb_data_storage_client: MongoDBDataStorage, data: dict[str, Any]):
        # Arrange

        # Act
        mongodb_data_storage_client.save_data(data)

        # Assert
        mongodb_data_storage_client.data_collection.insert_one.assert_called_once_with(data)

    @staticmethod
    def test_get_data(mongodb_data_storage_client: MongoDBDataStorage):
        # Arrange
        mock_cursor = MagicMock(spec=Cursor)
        mongodb_data_storage_client.data_collection.find.return_value = mock_cursor

        # Act
        returned_data = mongodb_data_storage_client.get_data()

        # Assert
        assert returned_data == list(mock_cursor)
        mongodb_data_storage_client.data_collection.find.assert_called_once_with({})

    @staticmethod
    def test_save_reasons_for_invalid_data(mongodb_data_storage_client: MongoDBDataStorage, invalidation_reasons: dict[str, Any]):
        # Arrange

        # Act
        mongodb_data_storage_client.save_reasons_for_invalid_data(invalidation_reasons)

        # Assert
        mongodb_data_storage_client.discard_collection.insert_one.assert_called_once_with(invalidation_reasons)

    @staticmethod
    def test_get_reasons_for_invalid_data(mongodb_data_storage_client: MongoDBDataStorage):
        # Arrange
        mock_cursor = MagicMock(spec=Cursor)
        mongodb_data_storage_client.discard_collection.find.return_value = mock_cursor

        # Act
        returned_data = mongodb_data_storage_client.get_reasons_for_invalid_data()

        # Assert
        assert returned_data == list(mock_cursor)
        mongodb_data_storage_client.discard_collection.find.assert_called_once_with({})

