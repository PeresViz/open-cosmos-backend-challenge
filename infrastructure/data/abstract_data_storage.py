import requests
from typing import Any

from abc import ABC, abstractmethod
from fastapi import HTTPException


class AbstractDataStorage(ABC):
    def fetch_data_from_server(self, port):
        url = f"http://localhost:{port}"  # Assuming the server is running locally
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            raise HTTPException(status_code=500, detail="Failed to fetch data from server")

    @abstractmethod
    def save_data(self, data: dict[str, Any]):
        ...

    @abstractmethod
    def get_data(self):
        ...

    @abstractmethod
    def save_discard_reasons(self, discard_reasons: list[dict[str, Any]]):
        ...

    @abstractmethod
    def get_discard_reasons(self):
        ...
