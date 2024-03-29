import json
from datetime import datetime, timedelta
from infrastructure.data.redis_data_storage import RedisDataStorage


class BusinessLogic:
    def __init__(self):
        self.data_storage = RedisDataStorage()

    def apply_business_rules(self, data):
        valid_data = []
        discard_reasons = []

        timestamp = data['time']
        if timestamp < (datetime.now() - timedelta(hours=1)).timestamp():
            discard_reasons.append({"timestamp": timestamp, "reason": "Data is too old"})
        if 'system' in data['tags'] or 'suspect' in data['tags']:
            discard_reasons.append({"timestamp": timestamp, "reason": "Data is system or suspect"})
        valid_data.append(data)

        return valid_data, discard_reasons

    def get_data_with_filters(self, start_time, end_time):
        data = self.data_storage.get_data()
        filtered_data = []

        for d in data:
            if start_time and d['time'] < start_time.timestamp():
                continue
            if end_time and d['time'] > end_time.timestamp():
                continue
            filtered_data.append(d)

        return filtered_data

    def process_and_store_data(self):
        data = self.data_storage.fetch_data_from_server(28462)
        if data:
            valid_data, discard_reasons = self.apply_business_rules(data)
            self.data_storage.process_data(valid_data)
            self.data_storage.save_discard_reasons(discard_reasons)

    def get_discard_reasons(self):
        return self.data_storage.get_discard_reasons()
