import redis
import json
import requests
from fastapi import HTTPException
from typing import Any
from infrastructure.data.abstract_data_storage import AbstractDataStorage


class RedisDataStorage(AbstractDataStorage):
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)

    def fetch_data_from_server(self, port):
        url = f"http://localhost:{port}"  # Assuming the server is running locally
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            raise HTTPException(status_code=500, detail="Failed to fetch data from server")

    def process_data(self, data: list[dict[str, Any]]):
        for d in data:
            self.redis_client.hset('data_store', d['time'], json.dumps(d))

    def get_data(self):
        data = self.redis_client.hgetall('data_store')
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
