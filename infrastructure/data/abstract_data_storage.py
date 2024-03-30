from typing import Any

from abc import ABC, abstractmethod


class AbstractDataStorage(ABC):

    @abstractmethod
    def save_data(self, data: dict[str, Any]):
        ...

    @abstractmethod
    def get_data(self):
        ...

    @abstractmethod
    def save_discard_reasons(self, discard_reasons: dict[str, Any]):
        ...

    @abstractmethod
    def get_discard_reasons(self):
        ...
