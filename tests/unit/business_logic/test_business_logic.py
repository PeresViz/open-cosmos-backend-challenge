import pytest
import struct
from unittest.mock import MagicMock, patch, call
from typing import Any
from datetime import datetime, timedelta
from pytest_lazyfixture import lazy_fixture

from business_logic.business_logic import BusinessLogic
from business_logic.constants import REASON_DATA_IS_TOO_OLD, SUSPECT_TAG, SYSTEM_TAG, REASON_DATA_IS_SYSTEM_OR_SUSPECT
from models.data import Data
from models.data_invalidation_reasons import DataInvalidationReasons


@pytest.fixture
def business_logic() -> BusinessLogic:
    return BusinessLogic(data_storage=MagicMock())


@pytest.fixture
def server_data() -> list[dict[str, Any]]:
    return [
        {"time": 1711644891, "value": [68, 51, 127, 191], "tags": []},
        {"time": 1711644891, "value": [68, 51, 127, 191], "tags": [SUSPECT_TAG]},
        {"time": 1711644991, "value": [68, 51, 127, 191], "tags": [SYSTEM_TAG]},
        {"time": 1711645991, "value": [68, 51, 127, 191], "tags": [SUSPECT_TAG, SYSTEM_TAG]}
    ]


@pytest.fixture
def invalidation_reasons() -> list[dict[str, Any]]:
    return [
        {"time": 1711644871, "reasons": [REASON_DATA_IS_TOO_OLD]},
        {"time": 1711644891, "reasons": [REASON_DATA_IS_SYSTEM_OR_SUSPECT]},
        {"time": 1711644991, "reasons": [REASON_DATA_IS_TOO_OLD, REASON_DATA_IS_SYSTEM_OR_SUSPECT]},
    ]


@pytest.fixture
def invalidation_reasons_with_time_in_iso_format(
        invalidation_reasons: list[dict[str, Any]]
) -> list[DataInvalidationReasons]:
    change_time_format = lambda d: {**d, "time": datetime.fromtimestamp(d["time"]).isoformat()}
    data = list(map(change_time_format, invalidation_reasons))
    return [DataInvalidationReasons(time=d['time'], reasons=d['reasons']) for d in data]


def change_time_and_value_format(data_dict: dict[str, Any]) -> dict[str, Any]:
    byte_value = bytes(data_dict["value"])
    decoded_value = struct.unpack('<f', byte_value)[0]
    return {
        **data_dict,
        "time": datetime.fromtimestamp(data_dict["time"]).isoformat(),
        "value": decoded_value
    }


@pytest.fixture
def data_with_time_in_iso_format(server_data: list[dict[str, Any]]) -> list[Data]:
    modified_data = [change_time_and_value_format(d) for d in server_data]
    return [Data(time=d['time'], value=d['value'], tags=d['tags']) for d in modified_data]


@pytest.fixture
def data_with_endtime_constraint(data_with_time_in_iso_format: list[Data]) -> list[Data]:
    return data_with_time_in_iso_format[:2]


@pytest.fixture
def invalidation_reasons_with_endtime_constraint(
        invalidation_reasons_with_time_in_iso_format: list[DataInvalidationReasons]
) -> list[DataInvalidationReasons]:
    return invalidation_reasons_with_time_in_iso_format[:2]


class TestBusinessLogic:
    @staticmethod
    @patch('infrastructure.clients.external_data_service.ExternalDataService.fetch_data_from_server')
    @patch('business_logic.business_logic.logging.getLogger')
    def test_fetch_data_from_server_when_exception_occurs(
            get_logger_mock: MagicMock,
            fetch_data_from_server_mock: MagicMock,
            business_logic: BusinessLogic
    ):
        # Arrange
        business_logic.logger = get_logger_mock
        fetch_data_from_server_mock.side_effect = Exception("An error occurred")

        # Act
        business_logic.fetch_data_from_server()

        # Assert
        business_logic.logger.info.assert_called_once_with("Fetching data from server...")
        business_logic.data_storage.save_data.assert_not_called()
        business_logic.data_storage.save_reasons_for_invalid_data.assert_not_called()
        business_logic.logger.error.assert_called_once_with("Error fetching data from server: An error occurred")
        business_logic.logger.warning.assert_not_called()

    @staticmethod
    @patch('infrastructure.clients.external_data_service.ExternalDataService.fetch_data_from_server')
    @patch('business_logic.business_logic.logging.getLogger')
    def test_fetch_data_from_server_when_server_returns_data_without_invalidation_reasons(
            get_logger_mock: MagicMock,
            fetch_data_from_server_mock: MagicMock,
            business_logic: BusinessLogic
    ):
        # Arrange
        business_logic.logger = get_logger_mock
        server_data = {"time": datetime.now().timestamp(), "value": [184, 240, 52, 191], "tags": []}
        fetch_data_from_server_mock.return_value = server_data

        # Act
        business_logic.fetch_data_from_server()

        # Assert
        business_logic.data_storage.save_data.assert_called_once_with(server_data)
        business_logic.data_storage.save_reasons_for_invalid_data.assert_not_called()
        business_logic.logger.info.assert_has_calls([call("Fetching data from server...")])
        business_logic.logger.error.assert_not_called()

    @staticmethod
    @patch('infrastructure.clients.external_data_service.ExternalDataService.fetch_data_from_server')
    @patch('business_logic.business_logic.logging.getLogger')
    def test_fetch_data_from_server_when_server_returns_data_with_invalidation_reasons(
            get_logger_mock: MagicMock,
            fetch_data_from_server_mock: MagicMock,
            business_logic: BusinessLogic
    ):
        # Arrange
        business_logic.logger = get_logger_mock
        data_time = (datetime.now() - timedelta(hours=2)).timestamp()
        server_data = {"time": data_time, "value": [184, 240, 52, 191], "tags": []}
        invalidation_reasons = {"time": data_time, "reasons": [REASON_DATA_IS_TOO_OLD]}
        fetch_data_from_server_mock.return_value = server_data

        # Act
        business_logic.fetch_data_from_server()

        # Assert
        business_logic.data_storage.save_data.assert_called_once_with(server_data)
        business_logic.data_storage.save_reasons_for_invalid_data.assert_called_once_with(invalidation_reasons)
        business_logic.logger.info.assert_has_calls(
            [
                call("Fetching data from server..."),
                call("Invalid data saved with reasons.")
            ]
        )
        business_logic.logger.error.assert_not_called()

    @staticmethod
    @patch('infrastructure.clients.external_data_service.ExternalDataService.fetch_data_from_server')
    @patch('business_logic.business_logic.logging.getLogger')
    def test_fetch_data_from_server_when_server_returns_no_data(
            get_logger_mock: MagicMock,
            fetch_data_from_server_mock: MagicMock,
            business_logic: BusinessLogic
    ):
        # Arrange
        business_logic.logger = get_logger_mock
        fetch_data_from_server_mock.return_value = {}

        # Act
        business_logic.fetch_data_from_server()

        # Assert
        business_logic.data_storage.save_data.assert_not_called()
        business_logic.data_storage.save_reasons_for_invalid_data.assert_not_called()
        business_logic.logger.info.assert_has_calls([call("Fetching data from server...")])
        business_logic.logger.warning.assert_has_calls([call("No data fetched from server.")])
        business_logic.logger.error.assert_not_called()

    @staticmethod
    @patch('business_logic.business_logic.logging.getLogger')
    def test_get_data_when_exception_occurs(
            get_logger_mock: MagicMock,
            business_logic: BusinessLogic
    ):
        # Arrange
        business_logic.logger = get_logger_mock
        business_logic.data_storage.get_data = MagicMock(side_effect=Exception("An error occurred"))

        # Act
        returned_data = business_logic.get_data()

        # Assert
        assert returned_data == []
        business_logic.data_storage.get_data.assert_called_once()
        business_logic.logger.error.assert_called_once_with(
            f"Error retrieving data from {type(business_logic.data_storage).__name__}: An error occurred"
        )

    @staticmethod
    @pytest.mark.parametrize(
        "start_time, end_time, return_data",
        [
            (
                    None,
                    None,
                    lazy_fixture("data_with_time_in_iso_format")
            ),
            (
                    datetime.strptime("2024-03-28T16:54:31", "%Y-%m-%dT%H:%M:%S"),
                    None,
                    lazy_fixture("data_with_time_in_iso_format")
            ),
            (
                    None,
                    datetime.strptime("2024-03-28T16:54:51", "%Y-%m-%dT%H:%M:%S"),
                    lazy_fixture("data_with_endtime_constraint")
            ),
            (
                    datetime.strptime("2024-03-28T16:54:31", "%Y-%m-%dT%H:%M:%S"),
                    datetime.strptime("2024-03-28T17:13:11", "%Y-%m-%dT%H:%M:%S"),
                    lazy_fixture("data_with_time_in_iso_format")
            ),
        ],
    )
    @patch('business_logic.business_logic.logging.getLogger')
    def test_get_data_on_success(
            get_logger_mock: MagicMock,
            server_data: list[dict[str, Any]],
            return_data: list[dict[str, Any]],
            business_logic: BusinessLogic,
            start_time: datetime,
            end_time: datetime
    ):
        # Arrange
        business_logic.logger = get_logger_mock
        business_logic.data_storage.get_data = MagicMock(return_value=server_data)

        # Act
        data = business_logic.get_data(start_time=start_time, end_time=end_time)

        # Assert
        assert data == return_data
        business_logic.data_storage.get_data.assert_called_once()
        business_logic.logger.info.assert_has_calls(
            [
                call(f"Retrieving data from {type(business_logic.data_storage).__name__}..."),
                call(f"Data retrieved successfully from {type(business_logic.data_storage).__name__}")
            ]
        )
        business_logic.logger.error.assert_not_called()

    @staticmethod
    @patch('business_logic.business_logic.logging.getLogger')
    def test_get_reasons_for_invalid_data_when_exception_occurs(
            get_logger_mock: MagicMock,
            business_logic: BusinessLogic
    ):
        # Arrange
        business_logic.logger = get_logger_mock
        business_logic.data_storage.get_reasons_for_invalid_data = MagicMock(side_effect=Exception("An error occurred"))

        # Act
        returned_data = business_logic.get_reasons_for_invalid_data()

        # Assert
        assert returned_data == []
        business_logic.data_storage.get_reasons_for_invalid_data.assert_called_once()
        business_logic.logger.error.assert_called_once_with(
            f"Error retrieving reasons for invalid data from {type(business_logic.data_storage).__name__}: An error occurred"
        )

    @staticmethod
    @pytest.mark.parametrize(
        "start_time, end_time, return_data",
        [
            (
                    None,
                    None,
                    lazy_fixture("invalidation_reasons_with_time_in_iso_format")
            ),
            (
                    datetime.strptime("2024-03-28T16:54:31", "%Y-%m-%dT%H:%M:%S"),
                    None,
                    lazy_fixture("invalidation_reasons_with_time_in_iso_format")
            ),
            (
                    None,
                    datetime.strptime("2024-03-28T16:54:51", "%Y-%m-%dT%H:%M:%S"),
                    lazy_fixture("invalidation_reasons_with_endtime_constraint")
            ),
            (
                    datetime.strptime("2024-03-28T16:54:31", "%Y-%m-%dT%H:%M:%S"),
                    datetime.strptime("2024-03-28T17:13:11", "%Y-%m-%dT%H:%M:%S"),
                    lazy_fixture("invalidation_reasons_with_time_in_iso_format")
            ),
        ],
    )
    @patch('business_logic.business_logic.logging.getLogger')
    def test_get_reasons_for_invalid_data_on_success(
            get_logger_mock: MagicMock,
            invalidation_reasons: list[dict[str, Any]],
            return_data: list[dict[str, Any]],
            business_logic: BusinessLogic,
            start_time: datetime,
            end_time: datetime
    ):
        # Arrange
        business_logic.logger = get_logger_mock
        business_logic.data_storage.get_reasons_for_invalid_data = MagicMock(return_value=invalidation_reasons)

        # Act
        data = business_logic.get_reasons_for_invalid_data(start_time=start_time, end_time=end_time)

        # Assert
        assert data == return_data
        business_logic.data_storage.get_reasons_for_invalid_data.assert_called_once()
        business_logic.logger.info.assert_has_calls(
            [
                call(f"Retrieving reasons for invalid data from {type(business_logic.data_storage).__name__}..."),
                call(f"Reasons for invalid data retrieved successfully from {type(business_logic.data_storage).__name__}")
            ]
        )
        business_logic.logger.error.assert_not_called()
