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

from ..exceptions import (
    EntityValidationError
)
from .types import (
    AdminType,
    AppType,
    GroupType,
    JobType,
    NarrativeType,
    ServiceType,
    UserType,
    WorkspaceType
)
from typing import (
    List,
    Dict,
    TypeVar
)

STR_SEPARATOR = "::"
E = TypeVar('E', bound='Entity')
TYPE_MAP = {
    "admin": AdminType,
    "app": AppType,
    "group": GroupType,
    "job": JobType,
    "narrative": NarrativeType,
    "service": ServiceType,
    "user": UserType,
    "workspace": WorkspaceType
}


class Entity(object):
    def __init__(self, e_id: str, e_type: str, name: str=None, auto_validate: str=False):
        """
        Instantiate a new Entity.
        If the type is bad, raises en EntityValidationError.
        If auto_validate is on, and the id is not found by the appropriate service, also
        raises an EntityValidationError.
        """
        assert e_id, "An Entity must have an id!"
        assert e_type and isinstance(e_type, str), "entity type must be a string"
        e_type = e_type.lower()
        self.set_type(e_type)  # sets self.type_obj, or raises an EntityValidationError
        self.type = e_type
        self.id = e_id
        self._name = name
        if auto_validate:
            v = self.validate()
            if not v:
                raise EntityValidationError(
                    "Entity of type {} with id {} is not valid".format(e_type, e_id)
                )

    def set_type(self, e_type: str) -> bool:
        """
        Simply validates the type by comparing it to a list of allowed types.
        If invalid, returns False. If fine, returns True.
        """
        if e_type not in TYPE_MAP:
            raise EntityValidationError(
                "'{}' is not a valid type for an Entity".format(e_type)
            )
        else:
            self.type_obj = TYPE_MAP[e_type]

    def validate(self) -> bool:
        """
        Validates the Entity by looking at its id and type.
        If the type is invalid, returns False.
        If the type is valid, then tries to validate the entity id against the service that
        maintains it. The workspace service for workspaces and narratives, for example.

        Each of the id validation calls return a boolean. But they can also raise
        an exception if their particular call fails. This is dire enough that the Entity
        being validated probably shouldn't be put in the notification DB, so we just let
        those percolate up.
        """
        return self.type_obj.validate_id(self.id)

    def to_dict(self, with_name: bool=False) -> Dict[str, str]:
        d = {
            "id": self.id,
            "type": self.type
        }
        if with_name and self._name is not None:
            d["name"] = self._name
        return d

    @classmethod
    def from_dict(cls, d: dict) -> E:
        assert isinstance(d, dict), "from_dict requires a dictionary input!"
        if "id" not in d:
            raise EntityValidationError("An Entity requires an id!")
        if "type" not in d:
            raise EntityValidationError("An Entity requires a type!")
        return cls(d["id"], d["type"], name=d.get("name"))

    @property
    def name(self) -> str:
        if self._name is None:
            self._fetch_name()
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    def _fetch_name(self) -> None:
        """
        Sets the name of this object based on its type.
        If anything fails, raises an EntityNameError.
        """
        self._name = self.type_obj.get_name_from_id(self.id)

    def __repr__(self):
        return "Entity(\"{}\", \"{}\")".format(self.id, self.type)

    def __str__(self):
        return "{}{}{}".format(self.type, STR_SEPARATOR, self.id)

    def __eq__(self, other):
        return other.id == self.id and other.type == self.type

    def __hash__(self):
        return hash((self.id, self.type))

    @classmethod
    def from_str(cls, s: str) -> E:
        """
        Given a string built with self.__str__(), this builds it back into an Entity.
        Doesn't do the validation, as it's expected to come from the database.
        Will raise an EntityValidationError
        """
        assert s and isinstance(s, str), "input must be a string."
        try:
            (t, i) = s.split(STR_SEPARATOR)
        except ValueError:
            raise EntityValidationError("'{}' could not be resolved into an Entity".format(s))
        return cls(i, t)

    @staticmethod
    def fetch_entity_names(entities: List[E]) -> None:
        """
        Uses various services to the names of all Entities in the given list.
        The goal here is to minimize the number of service calls. So if you have 100 Entities,
        it doesn't make 100 calls, but up to T calls, where T = number of unique types in that
        list of Entities (currently 5).

        Should be roughly O(n) (n = # of entities) operations, and O(T) (T = number of allowed
        Entity types) service calls, which will probably far outweigh everything else in the
        processing time being used.
        """
        # Steps.
        # 1. bin the entities by type
        # 2. for each bin:
        #   extract ids into a list
        #   run appropriate getter on that list
        #   set e.name = value for each
        # 3. done
        # 4. Raise exceptions when:
        #   lookups fail without warning
        # 5. Nulls are ok.

        # 1. Do the binning
        bins = dict()
        for t in TYPE_MAP:
            bins[t] = list()
        for e in entities:
            bins[e.type].append(e)
        # ...done

        # 2. Do the lookups
        for t in TYPE_MAP:
            id_list = list(set([e.id for e in bins[t]]))
            # run ids_to_names from whatever appropriate type
            ids_to_names = TYPE_MAP[t].get_names_from_ids(id_list)
            for e in bins[t]:
                print(e.type)
                print(e.id)
                if e.id in ids_to_names:
                    e.name = ids_to_names[e.id]

        # 3. done?
