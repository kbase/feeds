import abc
from typing import (
    List,
    Dict
)


class BaseType(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def get_name_from_id(i: str) -> str:
        """
        Should return the name as a str.
        If a fail happens, raise an EntityNameError
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def get_names_from_ids(ids: List[str]) -> Dict[str, str]:
        """
        Should return a dict with keys -> values = ids -> names.
        If any of them fail, set id -> None
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def validate_id(i: str) -> bool:
        """
        Shouldn't raise an Exception - just return False if it fails.
        """
        pass
