from typing import Any, Optional
from datetime import datetime, timedelta
from infrastructure.data.redis_data_storage import RedisDataStorage
from infrastructure.clients.external_data_service import ExternalDataService
from business_logic.constants import (
    SYSTEM_TAG,
    SUSPECT_TAG,
    REASON_DATA_IS_TOO_OLD,
    REASON_DATA_IS_SYSTEM_OR_SUSPECT,
)


class BusinessLogic:
    def __init__(self):
        self.data_storage = RedisDataStorage()

    def get_discard_reasons_from_server_data(self,
                                             data: dict[str, Any]
                                             ) -> list[Optional[dict[str, Any]]]:
        discard_reasons = []
        timestamp = data['time']

        if data['time'] < (datetime.now() - timedelta(hours=1)).timestamp():
            discard_reasons.append({"timestamp": timestamp, "reason": REASON_DATA_IS_TOO_OLD})

        if SYSTEM_TAG in data['tags'] or SUSPECT_TAG in data['tags']:
            discard_reasons.append({"timestamp": timestamp, "reason": REASON_DATA_IS_SYSTEM_OR_SUSPECT})

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

