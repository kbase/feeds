from .base import BaseType
from typing import (
    List,
    Dict
)
from feeds.external_api.workspace import (
    validate_narrative_id,
    get_narrative_name,
    get_narrative_names
)
from feeds.exceptions import (
    EntityNameError,
    WorkspaceError
)


class NarrativeType(BaseType):
    @staticmethod
    def get_name_from_id(i: str, token: str) -> str:
        try:
            name = get_narrative_name(i, token)
            if name is None:
                raise EntityNameError(
                    "Unable to find name for narrative id: {}".format(i)
                )
            return name
        except WorkspaceError as e:
            raise EntityNameError(e)

    @staticmethod
    def get_names_from_ids(ids: List[str], token: str) -> Dict[str, str]:
        return get_narrative_names(ids, token)

    @staticmethod
    def validate_id(i: str, token: str) -> bool:
        return validate_narrative_id(i, token)
