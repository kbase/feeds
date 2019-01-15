from .base import BaseType
from typing import (
    List,
    Dict
)
from feeds.external_api.catalog import (
    get_app_name,
    get_app_names
)
from feeds.exceptions import (
    CatalogError,
    EntityNameError
)


class AppType(BaseType):
    @staticmethod
    def get_name_from_id(i: str) -> str:
        """
        Should return the name as a str.
        If a fail happens, raise an EntityNameError
        """
        try:
            return get_app_name(i)
        except CatalogError as e:
            raise EntityNameError("Unable to find name for app id: {}".format(i))

    @staticmethod
    def get_names_from_ids(ids: List[str]) -> Dict[str, str]:
        """
        Should return a dict with keys -> values = ids -> names.
        If any of them fail, set id -> None
        """
        try:
            return get_app_names(ids)
        except CatalogError as e:
            raise EntityNameError("Unable to find app names: {}".format(str(e)))

    @staticmethod
    def validate_id(i: str) -> bool:
        """
        Shouldn't raise an Exception - just return False if it fails.
        """
        try:
            return get_app_name(i) is not None
        except CatalogError:
            return False
