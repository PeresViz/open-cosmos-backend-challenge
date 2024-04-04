import pymongo
from datetime import datetime
from typing import Any, Optional
from infrastructure.data.storage.abstract_data_storage import AbstractDataStorage
from infrastructure.data.storage.mongodb.constants import (
    MONGODB_CONNECTION_STRING,
    MONGODB_DATABASE_NAME,
    MONGODB_DATA_COLLECTION_NAME,
    MONGODB_DISCARD_COLLECTION_NAME,
)


class MongoDBDataStorage(AbstractDataStorage):
    def __init__(self):
        self.client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
        self.db = self.client[MONGODB_DATABASE_NAME]
        self.data_collection = self.db[MONGODB_DATA_COLLECTION_NAME]
        self.discard_collection = self.db[MONGODB_DISCARD_COLLECTION_NAME]

    def save_data(self, data: dict[str, Any]) -> None:
        self.data_collection.insert_one(data)

    def get_data(self, start_time: datetime = None, end_time: datetime = None) -> list[Optional[dict[str, Any]]]:
        query = self.__get_time_filter_query(start_time=start_time, end_time=end_time)
        data = self.data_collection.find(query)
        return list(data)

    def save_reasons_for_invalid_data(self, discard_reasons: dict[str, Any]) -> None:
        self.discard_collection.insert_one(discard_reasons)

    def get_reasons_for_invalid_data(self, start_time: datetime = None, end_time: datetime = None) \
            -> list[Optional[dict[str, Any]]]:
        query = self.__get_time_filter_query(start_time=start_time, end_time=end_time)
        discard_reasons = self.discard_collection.find(query)
        return list(discard_reasons)

    @staticmethod
    def __get_time_filter_query(start_time: datetime = None, end_time: datetime = None) -> dict[str, Any]:
        query = {}
        if start_time and end_time:
            query["time"] = {"$gte": start_time.timestamp(), "$lte": end_time.timestamp()}
        elif start_time:
            query["time"] = {"$gte": start_time.timestamp()}
        elif end_time:
            query["time"] = {"$lte": end_time.timestamp()}
        return query

