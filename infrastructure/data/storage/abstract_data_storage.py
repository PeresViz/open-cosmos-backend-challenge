from typing import Any, Optional

from abc import ABC, abstractmethod


class AbstractDataStorage(ABC):

    @abstractmethod
    def save_data(self, data: dict[str, Any]) -> None:
        ...

    @abstractmethod
    def get_data(self) -> list[Optional[dict[str, Any]]]:
        ...

    @abstractmethod
    def save_reasons_for_invalid_data(self, discard_reasons: dict[str, Any]) -> None:
        ...

    @abstractmethod
    def get_reasons_for_invalid_data(self) -> list[Optional[dict[str, Any]]]:
        ...
