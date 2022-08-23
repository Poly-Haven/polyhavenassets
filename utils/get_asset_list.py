import logging
import requests
from ..constants import REQ_HEADERS

log = logging.getLogger(__name__)


def get_asset_list(asset_type="all"):
    url = f"https://api.polyhaven.com/assets?t={asset_type}"
    res = requests.get(url, headers=REQ_HEADERS)

    if res.status_code != 200:
        error = f"Error retrieving asset list, status code: {res.status_code}"
        log.error(error)
        return (error, None)

    return (None, res.json())
