import bpy
import logging
import requests
from ..constants import REQ_HEADERS
from ..utils.early_access import early_access
from .. import __package__ as base_package

log = logging.getLogger(__name__)


def get_asset_list(asset_type="all"):
    url = f"https://api.polyhaven.com/assets?t={asset_type}"

    url += "&future=true" if early_access else ""

    verify_ssl = not bpy.context.preferences.addons[base_package].preferences.disable_ssl_verify
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

    return (None, res.json())
