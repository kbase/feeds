from .base import BaseType
from typing import (
    List,
    Dict
)
from feeds.external_api.auth import (
    validate_user_id,
    validate_user_ids
)
from feeds.exceptions import EntityNameError


class AdminType(BaseType):
    @staticmethod
    def get_name_from_id(i: str) -> str:
        if AdminType.validate_id(i):
            return "KBase"
        raise EntityNameError("Invalid admin account: {}".format(i))

    @staticmethod
    def get_names_from_ids(ids: List[str]) -> Dict[str, str]:
        return validate_user_ids(ids)

    @staticmethod
    def validate_id(i: str) -> bool:
        return validate_user_id(i)  # TODO
