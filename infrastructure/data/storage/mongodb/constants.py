import os

MONGODB_CONNECTION_STRING = f"{os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:6379')}"
MONGODB_DATABASE_NAME = f"{os.getenv('MONGODB_DATABASE_NAME', 'open-cosmos')}"
MONGODB_DATA_COLLECTION_NAME = f"{os.getenv('MONGODB_DATA_COLLECTION_NAME', 'data_collection')}"
MONGODB_DISCARD_COLLECTION_NAME = f"{os.getenv('MONGODB_DISCARD_COLLECTION_NAME', 'data_invalidation_reasons')}"
