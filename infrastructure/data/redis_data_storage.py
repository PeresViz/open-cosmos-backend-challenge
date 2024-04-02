import redis
import struct
import json
from typing import Any, Optional
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

    def save_data(self, data: dict[str, Any]) -> None:
        self.redis_client.hset(REDIS_DATA_HASH_KEY, data['time'], json.dumps(data))

    def get_data(self) -> list[Optional[dict[str, Any]]]:
        data = self.redis_client.hgetall(REDIS_DATA_HASH_KEY)
        all_data = []
        if data:
            for data_values in data.values():
                data_json = json.loads(data_values)

                # Convert the array of bytes to bytes object
                byte_value = bytes(data_json["value"])

                # Decode the bytes as a little-endian 32-bit float
                decoded_value = struct.unpack('<f', byte_value)[0]

                data_json['value'] = decoded_value
                all_data.append(data_json)
        return []

    def save_reasons_for_invalid_data(self, discard_reasons: dict[str, Any]) -> None:
        self.redis_client.hset(REDIS_DISCARD_REASONS_HASH_KEY, discard_reasons['time'], str(discard_reasons['reasons']))

    def get_reasons_for_invalid_data(self) -> list[Optional[dict[str, Any]]]:
        discard_reasons = self.redis_client.hgetall(REDIS_DISCARD_REASONS_HASH_KEY)
        reasons_list = []
        if discard_reasons:
            for time, reasons in discard_reasons.items():
                reasons_list.append({"time": time.decode(), "reasons": eval(reasons)})
        return reasons_list
