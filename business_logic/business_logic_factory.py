from business_logic.business_logic import BusinessLogic

from infrastructure.data.storage.mongodb.mongodb_data_storage import MongoDBDataStorage


class BusinessLogicFactory:
    @staticmethod
    def instantiate_business_logic() -> BusinessLogic:
        return BusinessLogic(data_storage=MongoDBDataStorage())
