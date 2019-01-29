from .base import BaseType
from typing import (
    List,
    Dict
)
from feeds.external_api.workspace import (
    validate_workspace_id,
    # get_workspace_name,
    # get_workspace_names
)
# from feeds.exceptions import (
#     EntityNameError,
#     WorkspaceError
# )
from .narrative import NarrativeType


# 1/29/2019 - Workspaces and Narratives are effectively interchangeable right now
# so Workspace "names" should just be narrative names.
#
# But I'm leaving in the commented code, just in case.

class WorkspaceType(BaseType):
    @staticmethod
    def get_name_from_id(i: str, token: str) -> str:
        return NarrativeType.get_name_from_id(i, token)
        # try:
        #     name = get_workspace_name(i, token)
        #     if name is None:
        #         raise EntityNameError(
        #             "Unable to find name for workspace id: {}".format(i)
        #         )
        #     return name
        # except WorkspaceError as e:
        #     raise EntityNameError(e)

    @staticmethod
    def get_names_from_ids(ids: List[str], token: str) -> Dict[str, str]:
        return NarrativeType.get_names_from_ids(ids, token)
        # try:
        #     return get_workspace_names(ids, token)
        # except WorkspaceError as e:
        #     raise EntityNameError(e)

    @staticmethod
    def validate_id(i: str, token: str) -> bool:
        return validate_workspace_id(i, token)
