from .base import BaseType
from typing import (
    List,
    Dict
)
from feeds.external_api.jobs import (
    validate_job_id,
    get_job_name
)
from feeds.exceptions import (
    EntityNameError,
    JobError
)


class JobType(BaseType):
    @staticmethod
    def get_name_from_id(i: str, token: str) -> str:
        try:
            name = get_job_name(i)
            if name is None:
                raise EntityNameError("Unable to find name for job id: {}".format(i))
            return name
        except JobError as e:
            raise EntityNameError(e)

    @staticmethod
    def get_names_from_ids(ids: List[str], token: str) -> Dict[str, str]:
        ret = dict()
        try:
            for j_id in ids:
                ret[j_id] = get_job_name(j_id)
            return ret
        except JobError as e:
            raise EntityNameError(str(e))

    @staticmethod
    def validate_id(i: str, token: str) -> bool:
        try:
            validate_job_id(i)
        except JobError as e:
            return False
