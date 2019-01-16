from .base import BaseType
from typing import (
    List,
    Dict
)
from feeds.external_api.workspace import (
    validate_workspace_id,
    get_workspace_name,
    get_workspace_names,
)
from feeds.exceptions import (
    EntityNameError,
    WorkspaceError
)


class WorkspaceType(BaseType):
    @staticmethod
    def get_name_from_id(i: str, token: str) -> str:
        try:
            name = get_workspace_name(i, token)
            if name is None:
                raise EntityNameError(
                    "Unable to find name for workspace id: {}".format(i)
                )
            return name
        except WorkspaceError as e:
            raise EntityNameError(e)

    @staticmethod
    def get_names_from_ids(ids: List[str], token: str) -> Dict[str, str]:
        try:
            return get_workspace_names(ids, token)
        except WorkspaceError as e:
            raise EntityNameError(e)

    @staticmethod
    def validate_id(i: str, token: str) -> bool:
        return validate_workspace_id(i, token)
