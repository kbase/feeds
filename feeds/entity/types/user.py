from .base import BaseType
from typing import (
    List,
    Dict
)
from feeds.external_api.auth import (
    validate_user_id,
    validate_user_ids
)
from requests import HTTPError
from feeds.exceptions import EntityNameError


class UserType(BaseType):
    @staticmethod
    def get_name_from_id(i: str) -> str:
        try:
            users = validate_user_ids([i])
            if i not in users:
                raise EntityNameError(
                    "Unable to find name for user id: {}".format(i)
                )
            else:
                return users[i]
        except HTTPError:
            raise EntityNameError(
                "Unable to find name for user id: {}".format(i)
            )

    @staticmethod
    def get_names_from_ids(ids: List[str]) -> Dict[str, str]:
        try:
            return validate_user_ids(ids)
        except HTTPError:
            raise EntityNameError(
                "Unable to find names for a bulk list of user ids!"
            )

    @staticmethod
    def validate_id(i: str) -> bool:
        return validate_user_id(i)
