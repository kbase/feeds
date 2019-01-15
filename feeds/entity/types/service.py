from .base import BaseType
from typing import (
    List,
    Dict
)

SERVICE_MAP = {
    "groups": "Groups",
    "groupsservice": "Groups",
    "jobs": "Jobs",
    "narrative": "Narrative",
    "workspace": "Workspace",
    "workspaceservice": "Workspace",
    "kbase": "KBase"
}

DEFAULT_SERVICE = "KBase"


class ServiceType(BaseType):
    @staticmethod
    def get_name_from_id(i: str) -> str:
        """
        Should return the name as a str.
        If a fail happens, raise an EntityNameError
        """
        # I don't care for making this hard coded, but if it should be
        # done, then this is the place.
        if i in SERVICE_MAP:
            return SERVICE_MAP[i]
        else:
            return DEFAULT_SERVICE

    @staticmethod
    def get_names_from_ids(ids: List[str]) -> Dict[str, str]:
        """
        Should return a dict with keys -> values = ids -> names.
        If any of them fail, set id -> None
        """
        names = dict()
        for i in ids:
            names[i] = ServiceType.get_name_from_id(i)
        return names

    @staticmethod
    def validate_id(i: str) -> bool:
        return i in SERVICE_MAP
