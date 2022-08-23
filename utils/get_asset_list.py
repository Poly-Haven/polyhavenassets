import logging
import requests
from pathlib import Path
from ..constants import REQ_HEADERS

log = logging.getLogger(__name__)


def get_asset_list(asset_type="all"):
    url = f"https://api.polyhaven.com/assets?t={asset_type}"

    early_access = (Path(__file__).parents[1] / "early_access.json").exists()
    url += "&future=true" if early_access else ""

    res = requests.get(url, headers=REQ_HEADERS)

    if res.status_code != 200:
        error = f"Error retrieving asset list, status code: {res.status_code}"
        log.error(error)
        return (error, None)

    return (None, res.json())
