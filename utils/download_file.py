import bpy
import logging
import requests
import threading
from pathlib import Path
from random import random
from time import sleep
from ..constants import REQ_HEADERS

log = logging.getLogger(__name__)

RES = {}


def get(url, key):
    global RES
    RES[key] = requests.get(url, headers=REQ_HEADERS)


def download_file(url, dest):
    key = url + str(random() * 1000000)
    log.info(f"Downloading {Path(url).name}")

    th = threading.Thread(target=get, kwargs={"url": url, "key": key})
    th.start()

    while th.is_alive() and not bpy.context.window_manager.pha_props.progress_cancel:
        sleep(0.1)

    if bpy.context.window_manager.pha_props.progress_cancel:
        msg = f"Cancelled {dest.name} mid-download"
        log.error(msg)
        return msg

    th.join()

    res = RES[key]
    if res.status_code != 200:
        msg = f"Error retrieving {url}, status code: {res.status_code}"
        log.error(msg)
        return msg

    dest.parent.mkdir(parents=True, exist_ok=True)

    with dest.open("wb") as f:
        f.write(res.content)

    return None
