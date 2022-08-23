import bpy
import logging
import requests
from pathlib import Path
from ..constants import REQ_HEADERS

log = logging.getLogger(__name__)


def download_file(url, dest):
    log.info(f"Downloading {Path(url).name}")

    res = requests.get(url, headers=REQ_HEADERS)
    if bpy.context.window_manager.pha_props.progress_cancel:
        return f"Cancelled {dest.name}"
    if res.status_code != 200:
        msg = f"Error retrieving {url}, status code: {res.status_code}"
        log.error(msg)
        return msg

    dest.parent.mkdir(parents=True, exist_ok=True)

    with dest.open("wb") as f:
        f.write(res.content)

    return None
