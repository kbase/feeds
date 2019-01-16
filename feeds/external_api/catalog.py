from feeds.biokbase.narrative_method_store.client import NarrativeMethodStore
from feeds.biokbase.narrative_method_store.baseclient import ServerError
from feeds.config import get_config
from typing import (
    List,
    Dict
)
from feeds.exceptions import CatalogError


def get_app_name(app_id: str) -> str:
    """
    Returns a single string - the Name of the given app id.
    Lookup errors raise a CatalogError
    """
    return get_app_names([app_id]).get(app_id)


def get_app_names(app_ids: List[str]) -> Dict[str, str]:
    """
    Expects ids to be of the form Module.Method (not Module/Method. Yeah, I know it's harder.)
    Returns a dict mapping from app id -> app name. Values are None if they
    don't exist. Errors during lookup will raise a CatalogError.
    """
    cfg = get_config()
    # maps from Mod.Meth app ids (provided by services) -> Mod/Meth app ids (used in lookup)
    # If the id is given as Mod/Meth, just maps to itself.
    slash_app_ids = dict()
    for app_id in app_ids:
        if '/' in app_id:
            slash_app_ids[app_id] = app_id
        else:
            slash_app_ids[app_id] = app_id.replace('.', '/')

    nms = NarrativeMethodStore(url=cfg.nms_url)
    try:
        names = dict()
        infos = nms.get_method_brief_info({"ids": list(set(slash_app_ids.values()))})
        for info in infos:
            if info is not None:
                names[info['id']] = info['name']
        ret_names = dict()
        for app_id in app_ids:
            ret_names[app_id] = names.get(slash_app_ids[app_id])
        return ret_names
    except ServerError as e:
        raise CatalogError("An error occurred while retrieving app names: {}".format(e.message))
