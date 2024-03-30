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

    def get_discard_reasons_from_server_data(self, data: dict[str, Any]) -> list[Optional[dict[str, Any]]]:
        discard_reasons = []
        timestamp = data['time']

        if self.__is_data_too_old(timestamp=timestamp):
            discard_reasons.append({"timestamp": timestamp, "reason": REASON_DATA_IS_TOO_OLD})

        if self.__is_data_system_or_suspect(data_tags=data['tags']):
            discard_reasons.append({"timestamp": timestamp, "reason": REASON_DATA_IS_SYSTEM_OR_SUSPECT})

        return discard_reasons

    def get_data_with_filters(self, start_time: datetime = None, end_time: datetime = None) -> list[dict[str, Any]]:
        data = self.data_storage.get_data()
        filtered_data = []

        for d in data:
            if self.__is_timestamp_within_time_range(
                timestamp=d['time'],
                start_time=start_time,
                end_time=end_time
            ):
                d['time'] = datetime.fromtimestamp(d['time']).isoformat()
                filtered_data.append(d)

        return filtered_data

    def fetch_data_from_server(self) -> None:
        server_data = ExternalDataService.fetch_data_from_server()
        if server_data:
            self.data_storage.save_data(server_data)
            discard_reasons = self.get_discard_reasons_from_server_data(server_data)
            if discard_reasons:
                self.data_storage.save_discard_reasons(discard_reasons)

    def get_discard_reasons(self) -> list[dict[str, Any]]:
        return self.data_storage.get_discard_reasons()

    @staticmethod
    def __is_timestamp_within_time_range(
            timestamp: int,
            start_time: datetime = None,
            end_time: datetime = None
    ) -> bool:
        return (start_time is None or timestamp >= start_time.timestamp()) \
               and \
               (end_time is None or timestamp <= end_time.timestamp())

    @staticmethod
    def __is_data_too_old(timestamp: int) -> bool:
        return timestamp < (datetime.now() - timedelta(hours=1)).timestamp()

    @staticmethod
    def __is_data_system_or_suspect(data_tags: list[str]) -> bool:
        return SYSTEM_TAG in data_tags or SUSPECT_TAG in data_tags


