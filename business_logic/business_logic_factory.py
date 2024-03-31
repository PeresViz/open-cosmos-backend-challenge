from business_logic.business_logic import BusinessLogic

from infrastructure.data.redis_data_storage import RedisDataStorage


class BusinessLogicFactory:
    @staticmethod
    def instantiate_business_logic():
        return BusinessLogic(data_storage=RedisDataStorage())
