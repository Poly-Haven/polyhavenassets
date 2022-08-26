import bpy
import logging
import requests
from ..constants import REQ_HEADERS
from ..utils.early_access import early_access

log = logging.getLogger(__name__)


def get_asset_list(asset_type="all"):
    url = f"https://api.polyhaven.com/assets?t={asset_type}"

    url += "&future=true" if early_access else ""

    verify_ssl = not bpy.context.preferences.addons["polyhavenassets"].preferences.disable_ssl_verify
    res = requests.get(url, headers=REQ_HEADERS, verify=verify_ssl)

    if res.status_code != 200:
        error = f"Error retrieving asset list, status code: {res.status_code}"
        log.error(error)
        return (error, None)

    return (None, res.json())
