"""
An entity is something with a type, id, and optional name, generally managed by some other service.
Examples are
* users - id, real name, and type=user as managed by auth
* groups - id, group name, and type=group, managed by groups
* narrative - id, name, and type=narrative, managed by workspace
* ...etc.
*
* The types are currently controlled.
* allowed = user, group, narrative, workspace, job
"""
from .external_api.auth import (
    validate_user_id,
    validate_user_ids
)
from .external_api.groups import (
    validate_group_id,
    get_group_names
)
from .external_api.workspace import (
    validate_workspace_id,
    get_workspace_name,
    get_narrative_name
)
from .external_api.jobs import (
    validate_job_id,
    get_job_name
)
from .exceptions import (
    EntityNameError,
    EntityValidationError,
    WorkspaceError,
    JobError
)
from typing import (
    Dict,
    TypeVar
)
from requests import HTTPError
STR_SEPARATOR = "::"
E = TypeVar('E', bound='Entity')


class Entity(object):
    def __init__(self, e_id: str, e_type: str, name: str=None, auto_validate: str=False):
        e_type = e_type.lower()
        if not self.validate_type(e_type):
            raise EntityValidationError(
                "'{}' is not a valid type for an Entity".format(e_type)
            )
        self.type = e_type
        self.id = e_id
        self.name = name
        if auto_validate:
            v = self.validate()
            if not v:
                raise EntityValidationError(
                    "Entity of type {} with id {} is not valid".format(e_type, e_id)
                )

    def validate_type(self, e_type: str) -> bool:
        return e_type in ['user', 'admin', 'group', 'narrative', 'workspace', 'job']

    def validate(self):
        if self.type == "user":
            return validate_user_id(self.id)
        elif self.type == "group":
            return validate_group_id(self.id)
        elif self.type == "workspace" or self.type == "narrative":
            return validate_workspace_id(self.id)
        elif self.type == "job":
            return validate_job_id(self.id)
        elif self.type == "admin":
            return True
        else:
            return False

    def to_dict(self, with_name: bool=False) -> Dict[str, str]:
        d = {
            "id": self.id,
            "type": self.type
        }
        if self.name is not None:
            d["name"] = self.name
        return d

    @classmethod
    def from_dict(cls, d: dict) -> E:
        if "id" not in d:
            raise EntityValidationError("An Entity requires an id!")
        if "type" not in d:
            raise EntityValidationError("An Entity requires a type!")
        return cls(d["id"], d["type"], name=d.get("name"))

    # @property
    # def name(self):
    #     return self.name

    # @name.setter
    # def name(self, name: str):
    #     self.name = name

    # @name.getter
    # def name(self) -> str:
    #     if self.name is None:
    #         self._fetch_name()
    #     return self.name

    def _fetch_name(self) -> None:
        """
        Sets the name of this object based on its type.
        If anything fails, raises an EntityNameError.
        """
        if self.type == "user":
            try:
                users = validate_user_ids([self.id])
                if self.id not in users:
                    raise EntityNameError(
                        "Unable to find name for user id: {}".format(self.id)
                    )
                else:
                    self.name = users[self.id]
            except HTTPError:
                raise EntityNameError(
                    "Unable to find name for user id: {}".format(self.id)
                )
        elif self.type == "group":
            try:
                groups = get_group_names([self.id])
                if self.id not in groups:
                    raise EntityNameError(
                        "Unable to find name for group id: {}".format(self.id)
                    )
                else:
                    self.name = groups[self.id]
            except HTTPError:
                raise EntityNameError("Unable to find name for group id: {}".format(self.id))
        elif self.type == "workspace":
            try:
                name = get_workspace_name(self.id)
                if name is not None:
                    self.name = name
                else:
                    raise EntityNameError(
                        "Unable to find name for workspace id: {}".format(self.id)
                    )
            except WorkspaceError as e:
                raise EntityNameError(e)
        elif self.type == "narrative":
            try:
                name = get_narrative_name(self.id)
                if name is not None:
                    self.name = name
                else:
                    raise EntityNameError(
                        "Unable to find name for narrative id: {}".format(self.id)
                    )
            except WorkspaceError as e:
                raise EntityNameError(e)
        elif self.type == "job":
            try:
                name = get_job_name(self.id)
                if name is not None:
                    self.name = name
                else:
                    raise EntityNameError("Unable to find name for job id: {}".format(self.id))
            except JobError as e:
                raise EntityNameError(e)
        elif self.type == "admin":
            self.name = "KBase"
        else:
            return

    def __repr__(self):
        return "Entity(\"{}\", \"{}\")".format(self.id, self.type)

    def __str__(self):
        return "{}{}{}".format(self.type, STR_SEPARATOR, self.id)

    @classmethod
    def from_str(cls, s: str) -> E:
        """
        Given a string built with self.__str__(), this builds it back into an Entity.
        Doesn't do the validation, as it's expected to come from the database.
        Will raise an EntityValidationError
        """
        try:
            (t, i) = s.split(STR_SEPARATOR)
        except ValueError:
            raise EntityValidationError("'{}' could not be resolved into an Entity".format(s))
        return cls(i, t)
