from typing import Any

from abc import ABC, abstractmethod


class AbstractDataStorage(ABC):

    @abstractmethod
    def save_data(self, data: dict[str, Any]) -> None:
        ...

    @abstractmethod
    def get_data(self) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    def save_discard_reasons(self, discard_reasons: dict[str, Any]) -> None:
        ...

    @abstractmethod
    def get_discard_reasons(self) -> list[dict[str, Any]]:
        ...
