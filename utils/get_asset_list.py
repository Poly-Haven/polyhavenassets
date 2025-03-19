import bpy
import json
import logging
import requests
from ..constants import REQ_HEADERS
from ..utils.abspath import abspath
from ..utils.early_access import early_access
from ..utils.get_asset_lib import get_asset_lib
from time import time
from .. import __package__ as base_package

log = logging.getLogger(__name__)


def get_asset_list(asset_type="all", force=False):
    """
    Get the asset list from our API.
    Cache it locally if it doesn't exist or if force is True.
    Cache expires after a week.
    """

    asset_lib = get_asset_lib(bpy.context)
    if asset_lib is None:
        error = 'First open Preferences > File Paths and create an asset library named "Poly Haven"'
        log.error(error)
        return (error if force else None, None)
    cache_file = abspath(asset_lib.path) / "asset_list_cache.json"
    cache_file.parent.mkdir(parents=True, exist_ok=True)

    if not force and cache_file.exists():
        days_old = (time() - cache_file.stat().st_mtime) / (60 * 60 * 24)
        if days_old > 7:
            # If cache is older than a week, force a refresh
            log.debug(f"Asset list cache expired ({days_old:.2f} days old), forcing refresh")
        else:
            # Otherwise get the cached data
            with open(cache_file, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    log.error("Error decoding asset list cache, forcing refresh")
                    data = None
            if data:
                log.debug(f"Using cached asset list ({days_old:.2f} days old)")
                return (None, data)

    url = f"https://api.polyhaven.com/assets?t={asset_type}"

    url += "&future=true" if early_access else ""

    verify_ssl = not bpy.context.preferences.addons[base_package].preferences.disable_ssl_verify
    log.debug(f"Getting asset list from {url}")
    try:
        res = requests.get(url, headers=REQ_HEADERS, verify=verify_ssl)
    except Exception as e:
        msg = f"[{type(e).__name__}] Error retrieving {url}"
        log.error(msg)
        return (msg, None)

    if res.status_code != 200:
        error = f"Error retrieving asset list, status code: {res.status_code}"
        log.error(error)
        return (error, None)

    # Cache data for next time
    with open(cache_file, "w") as f:
        json.dump(res.json(), f)

    return (None, res.json())
