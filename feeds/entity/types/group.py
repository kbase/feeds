from .base import BaseType
from typing import (
    List,
    Dict
)
from feeds.external_api.groups import (
    validate_group_id,
    get_group_names
)
from feeds.exceptions import (
    EntityNameError,
    GroupsError
)


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
        except GroupsError:
            raise EntityNameError("Unable to find name for group id: {}".format(i))

    @staticmethod
    def get_names_from_ids(ids: List[str], token: str) -> Dict[str, str]:
        try:
            return get_group_names(ids, token)
        except GroupsError:
            raise EntityNameError("Unable to find names for a list of group ids")

    @staticmethod
    def validate_id(i: str, token: str) -> bool:
        try:
            return validate_group_id(i)
        except GroupsError as e:
            return False
