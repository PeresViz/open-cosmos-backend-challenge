from typing import Any, Optional
import struct
import logging
from datetime import datetime, timedelta
from infrastructure.data.storage.abstract_data_storage import AbstractDataStorage
from infrastructure.clients.external_data_service import ExternalDataService
from business_logic.constants import (
    SYSTEM_TAG,
    SUSPECT_TAG,
    REASON_DATA_IS_TOO_OLD,
    REASON_DATA_IS_SYSTEM_OR_SUSPECT,
)
from business_logic.exceptions.failure_retrieving_data \
    import FailureRetrievingData
from business_logic.exceptions.failure_retrieving_invalid_data_reasons_exception \
    import FailureRetrievingInvalidDataReasonsException
from models.data import Data
from models.data_invalidation_reasons import DataInvalidationReasons


class BusinessLogic:
    def __init__(self, data_storage: AbstractDataStorage):
        self.data_storage = data_storage
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.StreamHandler())

    def fetch_data_from_server(self) -> None:
        try:
            self.logger.info("Fetching data from server...")
            server_data = ExternalDataService.fetch_data_from_server()

            if server_data:
                self.data_storage.save_data(server_data)

                invalid_data = self.__invalidate_data(server_data)

                if invalid_data:
                    self.data_storage.save_reasons_for_invalid_data(invalid_data)
                    self.logger.info("Invalid data saved with reasons.")
            else:
                self.logger.warning("No data fetched from server.")
        except Exception as e:
            self.logger.error(f"Error fetching data from server: {e}")

    def get_data(self, start_time: datetime = None, end_time: datetime = None) -> list[Optional[Data]]:
        try:
            self.logger.info("Retrieving data...")
            data = self.data_storage.get_data()

            data = self.__decode_value(data=data)

            data_with_time_filter = self.__apply_time_filter_to_data(
                data=data,
                start_time=start_time,
                end_time=end_time
            )

            self.logger.info("Data retrieved successfully")
            return [
                Data(time=d['time'], value=d['value'], tags=d['tags'])
                for d in data_with_time_filter
            ]
        except Exception as e:
            self.logger.error(f"Error retrieving data: {e}")
            raise FailureRetrievingData(
                f"Error retrieving data: {e}"
            )

    def get_reasons_for_invalid_data(
            self,
            start_time: datetime = None,
            end_time: datetime = None
    ) -> list[Optional[DataInvalidationReasons]]:
        try:
            self.logger.info("Retrieving reasons for invalid data...")

            discard_reasons = self.data_storage.get_reasons_for_invalid_data()

            discard_reasons = self.__decode_value(data=discard_reasons)

            discard_reasons_with_time_filter = self.__apply_time_filter_to_data(
                data=discard_reasons,
                start_time=start_time,
                end_time=end_time
            )

            self.logger.info("Reasons for invalid data retrieved successfully")
            return [
                DataInvalidationReasons(time=d['time'], value=d['value'], tags=d['tags'], reasons=d['reasons'])
                for d in discard_reasons_with_time_filter
            ]
        except Exception as e:
            self.logger.error(f"Error retrieving reasons for invalid data: {e}")
            raise FailureRetrievingInvalidDataReasonsException(
                f"Error retrieving reasons for invalid data: {e}"
            )

    def __invalidate_data(self, data: dict[str, Any]) -> dict[str, Any]:
        reasons = []

        if self.__is_data_too_old(timestamp=data['time']):
            reasons.append(REASON_DATA_IS_TOO_OLD)

        if self.__is_data_system_or_suspect(data_tags=data['tags']):
            reasons.append(REASON_DATA_IS_SYSTEM_OR_SUSPECT)

        return {"time": data['time'], "value": data["value"], "tags": data["tags"], "reasons": reasons} \
            if reasons else {}

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

    @staticmethod
    def __decode_value(data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        for d in data:
            # Convert the array of bytes to bytes object
            byte_value = bytes(d["value"])

            # Decode the bytes as a little-endian 32-bit float
            decoded_value = struct.unpack('<f', byte_value)[0]

            d['value'] = decoded_value
        return data



