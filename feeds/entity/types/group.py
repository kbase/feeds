from .base import BaseType
from typing import (
    List,
    Dict
)
from feeds.external_api.groups import (
    validate_group_id,
    get_group_names
)
from requests import HTTPError
from feeds.exceptions import EntityNameError


class GroupType(BaseType):
    @staticmethod
    def get_name_from_id(i: str, token: str) -> str:
        try:
            groups = get_group_names([i], token)
            if i not in groups:
                raise EntityNameError(
                    "Unable to find name for group id: {}".format(i)
                )
            else:
                return groups[i]
        except HTTPError:
            raise EntityNameError("Unable to find name for group id: {}".format(i))

    @staticmethod
    def get_names_from_ids(ids: List[str], token: str) -> Dict[str, str]:
        return get_group_names(ids, token)

    @staticmethod
    def validate_id(i: str, token: str) -> bool:
        return validate_group_id(i)
