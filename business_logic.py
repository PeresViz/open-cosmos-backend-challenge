from typing import Union, Optional
from datetime import datetime, timedelta
from infrastructure.data.redis_data_storage import RedisDataStorage
from infrastructure.clients.external_data_service import ExternalDataService


class BusinessLogic:
    def __init__(self):
        self.data_storage = RedisDataStorage()

    def get_discard_reasons_from_server_data(self,
                                             data: dict[str, Union[int, list[int], list[str]]]
                                             ) -> list[Optional[dict[str, Union[int, str]]]]:
        discard_reasons = []
        timestamp = data['time']

        if data['time'] < (datetime.now() - timedelta(hours=1)).timestamp():
            discard_reasons.append({"timestamp": timestamp, "reason": "Data is too old"})

        if 'system' in data['tags'] or 'suspect' in data['tags']:
            discard_reasons.append({"timestamp": timestamp, "reason": "Data is system or suspect"})

        return discard_reasons

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

    def fetch_data_from_server(self):
        server_data = ExternalDataService.fetch_data_from_server()
        if server_data:
            self.data_storage.save_data(server_data)
            discard_reasons = self.get_discard_reasons_from_server_data(server_data)
            if discard_reasons:
                self.data_storage.save_discard_reasons(discard_reasons)

    def get_discard_reasons(self):
        return self.data_storage.get_discard_reasons()

