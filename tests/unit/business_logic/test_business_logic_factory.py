from unittest.mock import patch, MagicMock

from business_logic.business_logic import BusinessLogic
from business_logic.business_logic_factory import BusinessLogicFactory


class TestBusinessLogicFactory:
    @staticmethod
    @patch("business_logic.business_logic_factory.RedisDataStorage")
    def test_instantiate_business_logic(redis_data_storage_mock: MagicMock):
        # Arrange

        # Act
        business_logic = BusinessLogicFactory.instantiate_business_logic()

        # Assert
        assert isinstance(business_logic, BusinessLogic)
        assert business_logic.data_storage == redis_data_storage_mock()
