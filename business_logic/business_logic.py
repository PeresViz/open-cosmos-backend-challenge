from typing import Any, Optional
from datetime import datetime, timedelta
from infrastructure.data.abstract_data_storage import AbstractDataStorage
from infrastructure.clients.external_data_service import ExternalDataService
from business_logic.constants import (
    SYSTEM_TAG,
    SUSPECT_TAG,
    REASON_DATA_IS_TOO_OLD,
    REASON_DATA_IS_SYSTEM_OR_SUSPECT,
)
from models.data import Data
from models.data_invalidation_reasons import DataInvalidationReasons


class BusinessLogic:
    def __init__(self, data_storage: AbstractDataStorage):
        self.data_storage = data_storage

    def fetch_data_from_server(self) -> None:
        server_data = ExternalDataService.fetch_data_from_server()
        if server_data:
            self.data_storage.save_data(server_data)
            invalid_data = self.__invalidate_data(server_data)
            if invalid_data:
                self.data_storage.save_reasons_for_invalid_data(invalid_data)

    def get_data(self, start_time: datetime = None, end_time: datetime = None) -> list[Optional[Data]]:
        data = self.data_storage.get_data()
        data_with_time_filter = self.__apply_time_filter_to_data(
            data=data,
            start_time=start_time,
            end_time=end_time
        )
        return [
            Data(time=d['time'], value=d['value'], tags=d['tags'])
            for d in data_with_time_filter
        ]

    def get_reasons_for_invalid_data(
            self,
            start_time: datetime = None,
            end_time: datetime = None
    ) -> list[Optional[DataInvalidationReasons]]:
        discard_reasons = self.data_storage.get_reasons_for_invalid_data()
        discard_reasons_with_time_filter = self.__apply_time_filter_to_data(
            data=discard_reasons,
            start_time=start_time,
            end_time=end_time
        )
        return [
            DataInvalidationReasons(time=d['time'], reasons=d['reasons'])
            for d in discard_reasons_with_time_filter
        ]

    def __invalidate_data(self, data: dict[str, Any]) -> dict[str, Any]:
        reasons = []

        if self.__is_data_too_old(timestamp=data['time']):
            reasons.append(REASON_DATA_IS_TOO_OLD)

        if self.__is_data_system_or_suspect(data_tags=data['tags']):
            reasons.append(REASON_DATA_IS_SYSTEM_OR_SUSPECT)

        return {"time": data['time'], "reasons": reasons} if reasons else {}

    def __apply_time_filter_to_data(
            self,
            data: list[dict[str, Any]],
            start_time: datetime = None,
            end_time: datetime = None
    ) -> list[dict[str, Any]]:
        filtered_data = []

        for d in data:
            d['time'] = int(d['time'])
            if self.__is_timestamp_within_time_range(
                timestamp=d['time'],
                start_time=start_time,
                end_time=end_time
            ):
                d['time'] = self.__unix_timestamp_to_iso8601_timestamp(unix_timestamp=d['time'])
                filtered_data.append(d)

        return filtered_data

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

    @staticmethod
    def __unix_timestamp_to_iso8601_timestamp(unix_timestamp: int):
        return datetime.fromtimestamp(unix_timestamp).isoformat()


