from unittest.mock import MagicMock
import pytest
from typing import Any
import json

from infrastructure.data.storage.redis.redis_data_storage import RedisDataStorage
from infrastructure.data.storage.redis.constants import REDIS_DATA_HASH_KEY, REDIS_DISCARD_REASONS_HASH_KEY


@pytest.fixture
def data() -> dict[str, Any]:
    return {"time": 1711644891, "value": [68, 51, 127, 191], "tags": []}


@pytest.fixture
def invalidation_reasons() -> dict[str, Any]:
    return {"time": 1711644891, "reasons": ["fake_reason"]}


@pytest.fixture
def redis_data_storage_client() -> RedisDataStorage:
    redis_client = RedisDataStorage()
    redis_client.redis_client = MagicMock()
    return redis_client


class TestRedisDataStorage:
    @staticmethod
    def test_save_data(redis_data_storage_client: RedisDataStorage, data: dict[str, Any]):
        # Arrange

        # Act
        redis_data_storage_client.save_data(data)

        # Assert
        redis_data_storage_client.redis_client.hset.assert_called_once_with(REDIS_DATA_HASH_KEY, data['time'], json.dumps(data))

    @staticmethod
    @pytest.mark.parametrize(
        "all_data, expected_data",
        [
            (
                    {b'1711644934': b'{"time": 1711644934, "value": [218, 202, 115, 191], "tags": []}'},
                    [{"time": 1711644934, "value": [218, 202, 115, 191], "tags": []}]
            ),
            (
                    {},
                    []
            ),
        ],
    )
    def test_get_data(
            all_data: dict[Any, Any],
            expected_data: dict[str, Any],
            redis_data_storage_client: RedisDataStorage
    ):
        # Arrange
        redis_data_storage_client.redis_client.hgetall.return_value = all_data

        # Act
        returned_data = redis_data_storage_client.get_data()

        # Assert
        assert returned_data == expected_data
        redis_data_storage_client.redis_client.hgetall.assert_called_once_with(REDIS_DATA_HASH_KEY)

    @staticmethod
    def test_save_reasons_for_invalid_data(redis_data_storage_client: RedisDataStorage, invalidation_reasons: dict[str, Any]):
        # Arrange

        # Act
        redis_data_storage_client.save_reasons_for_invalid_data(invalidation_reasons)

        # Assert
        redis_data_storage_client.redis_client.hset.assert_called_once_with(
            REDIS_DISCARD_REASONS_HASH_KEY,
            invalidation_reasons['time'],
            str(invalidation_reasons['reasons'])
        )


    @staticmethod
    @pytest.mark.parametrize(
        "reasons_for_data_invalidation, expected_return",
        [
            (
                    {b'1711644918': b"['Data is too old']"},
                    [{"time": '1711644918', "reasons": ['Data is too old']}]
            ),
            (
                    {},
                    []
            ),
        ],
    )
    def test_get_reasons_for_invalid_data(
            reasons_for_data_invalidation: dict[Any, Any],
            expected_return: dict[str, Any],
            redis_data_storage_client: RedisDataStorage
    ):
        # Arrange
        redis_data_storage_client.redis_client.hgetall.return_value = reasons_for_data_invalidation

        # Act
        returned_data = redis_data_storage_client.get_reasons_for_invalid_data()

        # Assert
        assert returned_data == expected_return
        redis_data_storage_client.redis_client.hgetall.assert_called_once_with(REDIS_DISCARD_REASONS_HASH_KEY)



