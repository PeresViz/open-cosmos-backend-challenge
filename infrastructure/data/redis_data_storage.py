import redis
import json
from typing import Any
from infrastructure.data.abstract_data_storage import AbstractDataStorage


class RedisDataStorage(AbstractDataStorage):
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)

    def save_data(self, data: dict[str, Any]):
        self.redis_client.hset('data', data['time'], json.dumps(data))

    def get_data(self):
        data = self.redis_client.hgetall('data')
        return [json.loads(data_json) for data_json in data.values()]

    def save_discard_reasons(self, discard_reasons: list[dict[str, Any]]):
        for discard_reason in discard_reasons:
            timestamp = discard_reason['timestamp']
            reason = discard_reason['reason']
            self.redis_client.hset('discard_reasons', timestamp, reason)

    def get_discard_reasons(self):
        discard_reasons = self.redis_client.hgetall('discard_reasons')
        reasons_list = [{"timestamp": timestamp.decode(), "reason": reason.decode()} for timestamp, reason in discard_reasons.items()]
        return reasons_list
