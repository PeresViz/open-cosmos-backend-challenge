import redis
import json
from typing import Any
from infrastructure.data.abstract_data_storage import AbstractDataStorage
from infrastructure.data.constants import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB_NUMBER,
    REDIS_DATA_HASH_KEY,
    REDIS_DISCARD_REASONS_HASH_KEY,
)


class RedisDataStorage(AbstractDataStorage):
    def __init__(self):
        self.redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB_NUMBER)

    def save_data(self, data: dict[str, Any]):
        self.redis_client.hset(REDIS_DATA_HASH_KEY, data['time'], json.dumps(data))

    def get_data(self):
        data = self.redis_client.hgetall(REDIS_DATA_HASH_KEY)
        return [json.loads(data_json) for data_json in data.values()]

    def save_discard_reasons(self, discard_reasons: dict[str, Any]):
        self.redis_client.hset(REDIS_DISCARD_REASONS_HASH_KEY, discard_reasons['time'], str(discard_reasons['reasons']))

    def get_discard_reasons(self):
        discard_reasons = self.redis_client.hgetall(REDIS_DISCARD_REASONS_HASH_KEY)
        reasons_list = [
            {"time": time.decode(), "reasons": eval(reasons)}
            for time, reasons in discard_reasons.items()
        ]
        return reasons_list
